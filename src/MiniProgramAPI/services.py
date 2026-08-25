import os
import uuid

import boto3
import requests
from django.conf import settings
from django.db import transaction
from django.db.models import Avg, Count, Sum
from django.utils import timezone

from CommunityAPI.miniprogram_api import is_text_invalid
from CommunityAPI.models import Content, Post, PostImage

from .constants import (
    AUDIT_APPROVED,
    AUDIT_PENDING,
    AUDIT_REJECTED,
    MESSAGE_COMMENT_POST,
    MESSAGE_AUDIT_REJECTED,
    MESSAGE_LIKE_COMMENT,
    MESSAGE_LIKE_POST,
    MESSAGE_LIKE_REVIEW,
    MESSAGE_REPLY_COMMENT,
)
from .exceptions import DependencyUnavailable
from .identity import public_user_summary
from .models import (
    Course,
    CourseReview,
    InteractionMessage,
    MiniProgramProfile,
    PostExtension,
    UploadAsset,
)


def milliseconds(value):
    if value is None:
        return None
    return int(value.timestamp() * 1000)


def current_content(post):
    prefetched = getattr(post, '_prefetched_objects_cache', {}).get('contents')
    if prefetched is not None:
        if not prefetched:
            return None
        return max(prefetched, key=lambda item: (item.editedTime, item.pk))
    return post.contents.order_by('-editedTime', '-id').prefetch_related('images').first()


def relation_contains_user(instance, relation_name, user_id):
    if not user_id:
        return False
    prefetched = getattr(instance, '_prefetched_objects_cache', {}).get(relation_name)
    if prefetched is not None:
        return any(item.user_id == user_id for item in prefetched)
    return getattr(instance, relation_name).filter(user_id=user_id).exists()


def post_kind(post):
    if post.replyToId_id is None:
        return 'post'
    if post.replyToComment_id is None:
        return 'comment'
    return 'reply'


def root_post(post):
    kind = post_kind(post)
    if kind == 'post':
        return post
    if kind == 'comment':
        return post.replyToId
    return post.replyToComment.replyToId


def get_extension(post):
    try:
        return post.mini_program_extension
    except PostExtension.DoesNotExist:
        return None


def is_public_post(post):
    extension = get_extension(post)
    return bool(
        extension
        and extension.audit_status == AUDIT_APPROVED
        and extension.deleted_at is None
        and not post.deleted
        and not post.censored
    )


def audit_text(profile, text, title=None):
    required = getattr(
        settings,
        'MINIPROGRAM_CONTENT_AUDIT_REQUIRED',
        not settings.DEBUG,
    )
    if not required:
        return AUDIT_APPROVED, ''

    mini_profile = MiniProgramProfile.objects.filter(user=profile).first()
    if not mini_profile or not mini_profile.wechat_openid:
        return AUDIT_PENDING, '等待绑定微信身份后审核'

    result = is_text_invalid(mini_profile.wechat_openid, text, title=title)
    if result is True:
        return AUDIT_REJECTED, '内容未通过安全审核'
    if result is False:
        return AUDIT_APPROVED, ''
    return AUDIT_PENDING, '内容安全服务暂不可用，等待重试'


def exchange_wechat_code(code):
    app_id = getattr(settings, 'MINIPROGRAM_APPID', '')
    app_secret = getattr(settings, 'MINIPROGRAM_SECRET', '')
    if not app_id or not app_secret:
        raise DependencyUnavailable('微信小程序登录配置尚未完成')
    try:
        response = requests.get(
            'https://api.weixin.qq.com/sns/jscode2session',
            params={
                'appid': app_id,
                'secret': app_secret,
                'js_code': code,
                'grant_type': 'authorization_code',
            },
            timeout=(3.05, 10),
        )
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise DependencyUnavailable('微信身份服务暂不可用') from exc

    if payload.get('errcode'):
        if int(payload['errcode']) in (40029, 40163):
            raise ValueError('微信登录凭证无效或已使用')
        raise DependencyUnavailable('微信身份服务暂不可用')
    openid = payload.get('openid')
    if not openid:
        raise DependencyUnavailable('微信身份服务返回结果不完整')
    return openid


def image_items(content, request):
    if not content:
        return []
    items = []
    for image in content.images.all():
        try:
            url = request.build_absolute_uri(image.image.url)
        except (ValueError, AttributeError):
            url = None
        items.append({
            'imageId': str(image.pk),
            'url': url,
            'thumbnailUrl': url,
        })
    return items


def serialize_post(post, request, detail=False):
    extension = get_extension(post)
    content = current_content(post)
    text = content.text if content else ''
    authenticated = bool(request.user and request.user.is_authenticated)
    user_id = request.user.pk if authenticated else None
    liked = relation_contains_user(post, 'mini_program_likes', user_id)
    mine = authenticated and post.createdBy_id == user_id
    anonymous = bool(extension and extension.is_anonymous)

    data = {
        'postId': str(post.pk),
        'author': public_user_summary(post.createdBy, anonymous=anonymous),
        'title': content.title if content else '',
        'images': image_items(content, request),
        'likeCount': extension.like_count if extension else 0,
        'commentCount': extension.comment_count if extension else 0,
        'isLiked': bool(liked),
        'isMine': bool(mine),
        'createdAt': milliseconds(post.createTime),
    }
    if detail:
        data['content'] = text
    else:
        data['summary'] = text[:80]
    if mine and extension:
        data['auditStatus'] = extension.audit_status
        data['auditMessage'] = extension.audit_message or None
    return data


def serialize_reply(reply, request, main_post):
    extension = get_extension(reply)
    content = current_content(reply)
    authenticated = bool(request.user and request.user.is_authenticated)
    user_id = request.user.pk if authenticated else None
    liked = relation_contains_user(reply, 'mini_program_likes', user_id)
    target = reply.replyToId
    data = {
        'commentId': str(reply.pk),
        'user': public_user_summary(reply.createdBy),
        'isAuthor': reply.createdBy_id == main_post.createdBy_id,
        'replyToUser': public_user_summary(target.createdBy) if target else None,
        'content': content.text if content else '',
        'likeCount': extension.like_count if extension else 0,
        'isLiked': bool(liked),
        'isMine': authenticated and reply.createdBy_id == user_id,
        'createdAt': milliseconds(reply.createTime),
    }
    return data


def serialize_comment(comment, request, include_replies=True):
    main_post = comment.replyToId
    extension = get_extension(comment)
    content = current_content(comment)
    authenticated = bool(request.user and request.user.is_authenticated)
    user_id = request.user.pk if authenticated else None
    liked = relation_contains_user(comment, 'mini_program_likes', user_id)
    replies = getattr(comment, '_public_replies', None)
    if replies is None:
        replies = list(Post.objects.filter(
            replyToComment=comment,
            deleted=False,
            censored=False,
            mini_program_extension__audit_status=AUDIT_APPROVED,
            mini_program_extension__deleted_at__isnull=True,
        ).select_related(
            'createdBy',
            'replyToId__createdBy',
            'mini_program_extension',
        ).prefetch_related('contents', 'mini_program_likes').order_by(
            'createTime', 'pk'
        ))

    data = {
        'commentId': str(comment.pk),
        'user': public_user_summary(comment.createdBy),
        'isAuthor': comment.createdBy_id == main_post.createdBy_id,
        'content': content.text if content else '',
        'likeCount': extension.like_count if extension else 0,
        'isLiked': bool(liked),
        'isMine': authenticated and comment.createdBy_id == user_id,
        'replyCount': len(replies),
        'createdAt': milliseconds(comment.createTime),
    }
    if include_replies:
        data['replies'] = [
            serialize_reply(reply, request, main_post)
            for reply in replies[:2]
        ]
    return data


def serialize_review(review, request):
    authenticated = bool(request.user and request.user.is_authenticated)
    user_id = request.user.pk if authenticated else None
    liked = relation_contains_user(review, 'likes', user_id)
    data = {
        'reviewId': str(review.pk),
        'user': public_user_summary(review.user, anonymous=review.is_anonymous),
        'rating': review.rating,
        'content': review.content,
        'likeCount': review.like_count,
        'isLiked': bool(liked),
        'isMine': authenticated and review.user_id == user_id,
        'createdAt': milliseconds(review.created_at),
        'updatedAt': milliseconds(review.updated_at),
    }
    if data['isMine']:
        data['auditStatus'] = review.audit_status
        data['auditMessage'] = review.audit_message or None
    return data


def create_message(recipient, sender, message_type, target_post=None,
                   root=None, target_review=None, snippet='', cover=''):
    if not recipient or (sender and recipient.pk == sender.pk):
        return None
    return InteractionMessage.objects.create(
        recipient=recipient,
        sender=sender,
        type=message_type,
        target_post=target_post,
        root_post=root,
        target_review=target_review,
        snippet=snippet[:120],
        cover=cover or '',
    )


def create_comment_message(comment):
    content = current_content(comment)
    snippet = content.text if content else ''
    if post_kind(comment) == 'comment':
        main = comment.replyToId
        return create_message(
            main.createdBy,
            comment.createdBy,
            MESSAGE_COMMENT_POST,
            target_post=comment,
            root=main,
            snippet=snippet,
        )

    target = comment.replyToId
    main = root_post(comment)
    return create_message(
        target.createdBy if target else None,
        comment.createdBy,
        MESSAGE_REPLY_COMMENT,
        target_post=comment,
        root=main,
        snippet=snippet,
    )


def create_like_message(profile, target_post=None, target_review=None):
    if target_post is not None:
        kind = post_kind(target_post)
        message_type = MESSAGE_LIKE_POST if kind == 'post' else MESSAGE_LIKE_COMMENT
        content = current_content(target_post)
        return create_message(
            target_post.createdBy,
            profile,
            message_type,
            target_post=target_post,
            root=root_post(target_post),
            snippet=content.text if content else '',
        )

    return create_message(
        target_review.user,
        profile,
        MESSAGE_LIKE_REVIEW,
        target_review=target_review,
        snippet=target_review.content,
    )


def create_audit_rejected_message(profile, target_post=None, target_review=None):
    if target_post is not None:
        content = current_content(target_post)
        return create_message(
            profile,
            None,
            MESSAGE_AUDIT_REJECTED,
            target_post=target_post,
            root=root_post(target_post),
            snippet=content.text if content else '',
        )
    return create_message(
        profile,
        None,
        MESSAGE_AUDIT_REJECTED,
        target_review=target_review,
        snippet=target_review.content if target_review else '',
    )


@transaction.atomic
def recalculate_course(course_id):
    course = Course.objects.select_for_update().get(pk=course_id)
    aggregates = CourseReview.objects.filter(
        course=course,
        deleted_at__isnull=True,
        audit_status=AUDIT_APPROVED,
    ).aggregate(
        rating_sum=Sum('rating'),
        rating_average=Avg('rating'),
        review_count=Count('id'),
    )
    course.rating_sum = aggregates['rating_sum'] or 0
    course.rating_average = aggregates['rating_average'] or 0
    course.review_count = aggregates['review_count'] or 0
    course.save(update_fields=['rating_sum', 'rating_average', 'review_count'])
    return course


def rating_distribution(course):
    rows = CourseReview.objects.filter(
        course=course,
        deleted_at__isnull=True,
        audit_status=AUDIT_APPROVED,
    ).values('rating').annotate(total=Count('id'))
    distribution = {str(value): 0 for value in range(1, 6)}
    for row in rows:
        distribution[str(row['rating'])] = row['total']
    return distribution


def storage_client():
    endpoint_url = getattr(settings, 'AWS_S3_ENDPOINT_URL', None)
    access_key = getattr(settings, 'AWS_ACCESS_KEY_ID', None)
    secret_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)
    bucket = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None)
    if not all((endpoint_url, access_key, secret_key, bucket)):
        raise DependencyUnavailable('对象存储尚未配置')
    client = boto3.client(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )
    return client, bucket


def create_upload_token(profile, filename, content_type, size):
    extension = os.path.splitext(filename or '')[1].lower()
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
    allowed_types = {'image/jpeg', 'image/png', 'image/webp'}
    if extension not in allowed_extensions or content_type not in allowed_types:
        raise ValueError('不支持的图片格式')
    if size <= 0 or size > 10 * 1024 * 1024:
        raise ValueError('图片大小必须在 1 字节到 10 MB 之间')

    relative_key = 'uploads/community/{}/{}/{}{}'.format(
        profile.pk,
        timezone.now().strftime('%Y/%m'),
        uuid.uuid4(),
        extension,
    )
    media_location = getattr(settings, 'AWS_MEDIA_LOCATION', 'media').strip('/')
    object_key = '{}/{}'.format(media_location, relative_key)
    client, bucket = storage_client()
    signed = client.generate_presigned_post(
        Bucket=bucket,
        Key=object_key,
        Fields={'Content-Type': content_type},
        Conditions=[
            {'Content-Type': content_type},
            ['content-length-range', 1, 10 * 1024 * 1024],
        ],
        ExpiresIn=600,
    )
    return {
        'method': 'POST',
        'host': signed['url'],
        'objectKey': object_key,
        'fields': signed['fields'],
        'expire': milliseconds(timezone.now() + timezone.timedelta(minutes=10)),
    }


def complete_upload(profile, object_key, content_type, expected_size):
    media_location = getattr(settings, 'AWS_MEDIA_LOCATION', 'media').strip('/')
    expected_prefix = '{}/uploads/community/{}/'.format(media_location, profile.pk)
    if not object_key.startswith(expected_prefix):
        raise ValueError('上传对象不属于当前用户')

    existing = UploadAsset.objects.filter(
        uploader=profile,
        object_key=object_key,
    ).select_related('image').first()
    if existing:
        if existing.content_type != content_type or existing.size != expected_size:
            raise ValueError('上传完成参数与首次确认不一致')
        return existing.image, existing.audit_status

    client, bucket = storage_client()
    try:
        head = client.head_object(Bucket=bucket, Key=object_key)
    except Exception as exc:
        raise DependencyUnavailable('无法确认上传对象') from exc

    actual_size = int(head.get('ContentLength') or 0)
    actual_type = head.get('ContentType') or content_type
    if actual_size != expected_size or actual_size > 10 * 1024 * 1024:
        raise ValueError('上传文件大小校验失败')
    if actual_type not in {'image/jpeg', 'image/png', 'image/webp'}:
        raise ValueError('上传文件类型校验失败')

    relative_key = object_key[len(media_location) + 1:]
    image_id = uuid.uuid4()
    image = PostImage.objects.create(
        id=image_id,
        image=relative_key,
        uploader=profile,
    )
    audit_status = AUDIT_APPROVED if not getattr(
        settings, 'MINIPROGRAM_IMAGE_AUDIT_REQUIRED', not settings.DEBUG
    ) else AUDIT_PENDING
    UploadAsset.objects.create(
        image=image,
        uploader=profile,
        object_key=object_key,
        content_type=actual_type,
        size=actual_size,
        audit_status=audit_status,
    )
    return image, audit_status
