import math
import uuid

from django.core import signing
from django.db import IntegrityError, transaction
from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.response import Response

from CommunityAPI.models import Content, Post
from UserAuthAPI.models import UserProfile

from .base import AuthenticatedV1APIView, IdempotentCreateMixin, PublicV1APIView
from .constants import (
    AUDIT_APPROVED,
    AUDIT_REJECTED,
    LIKE_COMMENT,
    LIKE_POST,
    LIKE_REVIEW,
    MESSAGE_AUDIT_REJECTED,
    MESSAGE_COMMENT_POST,
    MESSAGE_LIKE_COMMENT,
    MESSAGE_LIKE_POST,
    MESSAGE_LIKE_REVIEW,
    MESSAGE_REPLY_COMMENT,
    SECTION_CONFESSION_WALL,
)
from .exceptions import DuplicateOperation, OperationTooFrequent
from .identity import profile_identity, public_user_summary
from .models import (
    Course,
    CourseReview,
    CourseReviewLike,
    InteractionMessage,
    MiniProgramProfile,
    PostExtension,
    PostLike,
    UploadAsset,
)
from .pagination import V1CursorPagination
from .serializers import (
    CreateCommentSerializer,
    CreateCourseSerializer,
    CreatePostSerializer,
    LikeToggleSerializer,
    MessageReadSerializer,
    ReviewSerializer,
    UploadCompleteSerializer,
    UploadTokenSerializer,
    WechatBindSerializer,
)
from .services import (
    audit_text,
    complete_upload,
    create_audit_rejected_message,
    create_comment_message,
    create_like_message,
    create_upload_token,
    current_content,
    exchange_wechat_code,
    get_extension,
    image_items,
    is_public_post,
    milliseconds,
    post_kind,
    rating_distribution,
    recalculate_course,
    root_post,
    serialize_comment,
    serialize_post,
    serialize_reply,
    serialize_review,
)


def paginate(request, queryset, serializer, ordering):
    paginator = V1CursorPagination()
    paginator.ordering = ordering
    page = paginator.paginate_queryset(queryset, request)
    return paginator.data([serializer(instance) for instance in page])


def public_main_posts():
    return Post.objects.filter(
        replyToId__isnull=True,
        replyToComment__isnull=True,
        deleted=False,
        censored=False,
        mini_program_extension__audit_status=AUDIT_APPROVED,
        mini_program_extension__deleted_at__isnull=True,
        mini_program_extension__section=SECTION_CONFESSION_WALL,
    ).select_related(
        'createdBy',
        'createdBy__mini_program_profile',
        'createdBy__userinformation',
        'mini_program_extension',
    ).prefetch_related(
        'contents__images',
        'mini_program_likes',
    )


def public_reviews(course=None):
    queryset = CourseReview.objects.filter(
        deleted_at__isnull=True,
        audit_status=AUDIT_APPROVED,
        course__deleted_at__isnull=True,
    ).select_related(
        'user',
        'user__mini_program_profile',
        'user__userinformation',
        'course',
    ).prefetch_related('likes')
    if course is not None:
        queryset = queryset.filter(course=course)
    return queryset


def parse_post_id(value, field='id'):
    try:
        return int(value)
    except (TypeError, ValueError):
        raise serializers.ValidationError({field: 'ID 格式不正确'})


def parse_uuid(value, field='id'):
    try:
        return uuid.UUID(str(value))
    except (TypeError, ValueError, AttributeError):
        raise serializers.ValidationError({field: 'ID 格式不正确'})


def decode_merged_cursor(value):
    if not value:
        return 0
    try:
        payload = signing.loads(value, salt='mini-program-likes-cursor', max_age=86400)
        offset = int(payload['offset'])
        if offset < 0:
            raise ValueError
        return offset
    except (signing.BadSignature, KeyError, TypeError, ValueError):
        raise serializers.ValidationError({'cursor': '游标无效或已过期'})


def encode_merged_cursor(offset):
    return signing.dumps(
        {'offset': offset},
        salt='mini-program-likes-cursor',
        compress=True,
    )


class HealthView(PublicV1APIView):
    authentication_classes = ()

    def get(self, request):
        return Response({'status': 'ok'})


class WechatBindView(AuthenticatedV1APIView):
    def post(self, request):
        serializer = WechatBindSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            openid = exchange_wechat_code(serializer.validated_data['code'])
        except ValueError as exc:
            raise serializers.ValidationError({'code': str(exc)})

        profile = self.get_profile()
        with transaction.atomic():
            UserProfile.objects.select_for_update().get(pk=profile.pk)
            conflict = MiniProgramProfile.objects.select_for_update().filter(
                wechat_openid=openid,
            ).exclude(user=profile).exists()
            if conflict:
                raise DuplicateOperation('该微信身份已绑定其他 CSSANet 账号')
            mini_profile, _ = MiniProgramProfile.objects.update_or_create(
                user=profile,
                defaults={'wechat_openid': openid},
            )
        return Response({
            'wechatBound': True,
            'updatedAt': milliseconds(mini_profile.updated_at),
        })


class UploadTokenView(AuthenticatedV1APIView):
    def get(self, request):
        serializer = UploadTokenSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        profile = self.get_profile()
        try:
            data = create_upload_token(
                profile,
                serializer.validated_data['filename'],
                serializer.validated_data['contentType'],
                serializer.validated_data['size'],
            )
        except ValueError as exc:
            raise serializers.ValidationError(str(exc))
        return Response(data)


class UploadCompleteView(AuthenticatedV1APIView):
    @transaction.atomic
    def post(self, request):
        serializer = UploadCompleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = self.get_profile()
        UserProfile.objects.select_for_update().get(pk=profile.pk)
        try:
            image, audit_status = complete_upload(
                profile,
                serializer.validated_data['objectKey'],
                serializer.validated_data['contentType'],
                serializer.validated_data['size'],
            )
        except ValueError as exc:
            raise serializers.ValidationError(str(exc))
        try:
            url = request.build_absolute_uri(image.image.url)
        except ValueError:
            url = None
        return Response({
            'imageId': str(image.pk),
            'url': url,
            'thumbnailUrl': url,
            'auditStatus': audit_status,
        }, status=status.HTTP_201_CREATED)


class MeView(AuthenticatedV1APIView):
    def get(self, request):
        profile = self.get_profile()
        identity = profile_identity(profile)
        post_ids = Post.objects.filter(
            createdBy=profile,
            deleted=False,
            mini_program_extension__deleted_at__isnull=True,
        )
        post_count = post_ids.filter(replyToId__isnull=True).count()
        comment_count = post_ids.filter(replyToId__isnull=False).count()
        likes_on_posts = PostLike.objects.filter(post__createdBy=profile).count()
        likes_on_reviews = CourseReviewLike.objects.filter(review__user=profile).count()
        unread_count = InteractionMessage.objects.filter(
            recipient=profile,
            is_read=False,
        ).count()
        return Response({
            'userId': identity['userId'],
            'nickname': identity['nickname'],
            'avatar': identity['avatar'],
            'college': identity['college'],
            'postCount': post_count,
            'commentCount': comment_count,
            'likeReceivedCount': likes_on_posts + likes_on_reviews,
            'unreadCount': unread_count,
            'wechatBound': MiniProgramProfile.objects.filter(
                user=profile,
                wechat_openid__isnull=False,
            ).exists(),
        })


class MyPostsView(AuthenticatedV1APIView):
    def get(self, request):
        profile = self.get_profile()
        queryset = Post.objects.filter(
            createdBy=profile,
            replyToId__isnull=True,
            deleted=False,
            mini_program_extension__deleted_at__isnull=True,
        ).select_related(
            'createdBy',
            'createdBy__mini_program_profile',
            'createdBy__userinformation',
            'mini_program_extension',
        ).prefetch_related(
            'contents__images',
            'mini_program_likes',
        )
        audit_status = request.query_params.get('auditStatus', 'all')
        if audit_status not in ('all', 'PENDING', 'APPROVED', 'REJECTED'):
            raise serializers.ValidationError({
                'auditStatus': '只支持 all、PENDING、APPROVED 或 REJECTED',
            })
        if audit_status != 'all':
            queryset = queryset.filter(mini_program_extension__audit_status=audit_status)

        def item(post):
            data = serialize_post(post, request)
            extension = post.mini_program_extension
            data.update({
                'isAnonymous': extension.is_anonymous,
                'auditStatus': extension.audit_status,
                'auditMessage': extension.audit_message or None,
            })
            return data

        return Response(paginate(request, queryset, item, ('-createTime', '-pk')))


class MyCommentsView(AuthenticatedV1APIView):
    def get(self, request):
        profile = self.get_profile()
        queryset = Post.objects.filter(
            createdBy=profile,
            replyToId__isnull=False,
            deleted=False,
            mini_program_extension__deleted_at__isnull=True,
        ).select_related(
            'createdBy',
            'replyToId',
            'replyToComment__replyToId',
            'mini_program_extension',
        ).prefetch_related('contents')

        def item(comment):
            content = current_content(comment)
            main = root_post(comment)
            main_content = current_content(main)
            extension = comment.mini_program_extension
            return {
                'commentId': str(comment.pk),
                'content': content.text if content else '',
                'postId': str(main.pk),
                'postTitle': main_content.title if main_content else '',
                'likeCount': extension.like_count,
                'auditStatus': extension.audit_status,
                'createdAt': milliseconds(comment.createTime),
            }

        return Response(paginate(request, queryset, item, ('-createTime', '-pk')))


class MyLikesReceivedView(AuthenticatedV1APIView):
    def get(self, request):
        profile = self.get_profile()
        queryset = InteractionMessage.objects.filter(
            recipient=profile,
            type__in=(MESSAGE_LIKE_POST, MESSAGE_LIKE_COMMENT, MESSAGE_LIKE_REVIEW),
        ).select_related(
            'sender',
            'sender__mini_program_profile',
            'sender__userinformation',
            'target_post',
            'root_post',
            'target_review',
        )
        kind = request.query_params.get('type', 'all')
        mapping = {
            'post': MESSAGE_LIKE_POST,
            'comment': MESSAGE_LIKE_COMMENT,
            'review': MESSAGE_LIKE_REVIEW,
        }
        if kind not in ('all', *mapping.keys()):
            raise serializers.ValidationError({
                'type': '只支持 all、post、comment 或 review',
            })
        if kind in mapping:
            queryset = queryset.filter(type=mapping[kind])
        return Response(paginate(
            request,
            queryset,
            lambda message: serialize_message(message),
            ('-id',),
        ))


class MyLikesGivenView(AuthenticatedV1APIView):
    def get(self, request):
        profile = self.get_profile()
        kind_value = request.query_params.get('type', 'all')
        kind_mapping = {
            'all': 'all',
            str(LIKE_POST): LIKE_POST,
            str(LIKE_COMMENT): LIKE_COMMENT,
            str(LIKE_REVIEW): LIKE_REVIEW,
        }
        if kind_value not in kind_mapping:
            raise serializers.ValidationError({
                'type': '只支持 all、1、2 或 3',
            })
        kind = kind_mapping[kind_value]
        post_likes = PostLike.objects.filter(user=profile).select_related(
            'post',
            'post__replyToId',
            'post__replyToComment__replyToId',
        )
        review_likes = CourseReviewLike.objects.filter(user=profile).select_related(
            'review',
            'review__course',
        )
        # A merged cursor over two tables is not stable. This endpoint uses the
        # newest records from both sources and emits a time-based opaque cursor
        # only after materialising the small personal result set.
        items = []
        for like in post_likes.prefetch_related(
            'post__contents',
            'post__replyToId__contents',
            'post__replyToComment__replyToId__contents',
        ):
            post = like.post
            target_type = LIKE_POST if post_kind(post) == 'post' else LIKE_COMMENT
            if kind not in ('all', target_type):
                continue
            if not is_public_post(post):
                continue
            main = root_post(post)
            if main is None or not is_public_post(main):
                continue
            content = current_content(post)
            main_content = current_content(main)
            items.append({
                'likeId': 'post:{}'.format(like.pk),
                'targetType': LIKE_POST if post_kind(post) == 'post' else LIKE_COMMENT,
                'targetId': str(post.pk),
                'postId': str(main.pk),
                'title': main_content.title if main_content else '',
                'snippet': (content.text if content else '')[:80],
                'cover': None,
                'createdAt': milliseconds(like.created_at),
                '_created_at': like.created_at,
            })
        for like in review_likes:
            if kind not in ('all', LIKE_REVIEW):
                continue
            review = like.review
            if (
                review.deleted_at is not None
                or review.audit_status != AUDIT_APPROVED
                or review.course.deleted_at is not None
            ):
                continue
            items.append({
                'likeId': 'review:{}'.format(like.pk),
                'targetType': LIKE_REVIEW,
                'targetId': str(review.pk),
                'postId': None,
                'title': review.course.name,
                'snippet': review.content[:80],
                'cover': None,
                'createdAt': milliseconds(like.created_at),
                '_created_at': like.created_at,
            })
        items.sort(key=lambda item: item['_created_at'], reverse=True)
        try:
            size = int(request.query_params.get('size', 20))
        except (TypeError, ValueError):
            raise serializers.ValidationError({'size': '必须是整数'})
        size = min(max(size, 1), 50)
        offset = decode_merged_cursor(request.query_params.get('cursor'))
        page = items[offset:offset + size]
        for item in page:
            item.pop('_created_at', None)
        next_offset = offset + len(page)
        return Response({
            'list': page,
            'nextCursor': (
                encode_merged_cursor(next_offset)
                if next_offset < len(items) else None
            ),
            'hasMore': next_offset < len(items),
        })


class MyReviewsView(AuthenticatedV1APIView):
    def get(self, request):
        profile = self.get_profile()
        queryset = CourseReview.objects.filter(
            user=profile,
            deleted_at__isnull=True,
        ).select_related('course')

        def item(review):
            return {
                'reviewId': str(review.pk),
                'courseId': str(review.course_id),
                'courseName': review.course.name,
                'teacher': review.course.teacher,
                'rating': review.rating,
                'content': review.content,
                'isAnonymous': review.is_anonymous,
                'auditStatus': review.audit_status,
                'createdAt': milliseconds(review.created_at),
                'updatedAt': milliseconds(review.updated_at),
            }

        return Response(paginate(request, queryset, item, ('-created_at', '-id')))


def serialize_message(message):
    type_text = {
        MESSAGE_LIKE_POST: '赞了你的帖子',
        MESSAGE_LIKE_COMMENT: '赞了你的评论',
        MESSAGE_LIKE_REVIEW: '赞了你的课程评价',
        MESSAGE_COMMENT_POST: '评论了你的帖子',
        MESSAGE_REPLY_COMMENT: '回复了你的评论',
        MESSAGE_AUDIT_REJECTED: '你的内容未通过审核',
    }
    target_post = message.target_post
    target_review = message.target_review
    comment_id = None
    post_id = None
    if target_post:
        post_id = str(message.root_post_id or target_post.pk)
        if post_kind(target_post) != 'post':
            comment_id = str(target_post.pk)
    return {
        'messageId': str(message.pk),
        'type': message.type,
        'typeText': type_text.get(message.type, message.type),
        'sender': public_user_summary(message.sender) if message.sender else None,
        'postId': post_id,
        'commentId': comment_id,
        'reviewId': str(target_review.pk) if target_review else None,
        'courseId': str(target_review.course_id) if target_review else None,
        'snippet': message.snippet,
        'cover': message.cover or None,
        'isRead': message.is_read,
        'createdAt': milliseconds(message.created_at),
    }


def message_filter(queryset, kind):
    if kind == 'like':
        return queryset.filter(type__in=(
            MESSAGE_LIKE_POST,
            MESSAGE_LIKE_COMMENT,
            MESSAGE_LIKE_REVIEW,
        ))
    if kind == 'comment':
        return queryset.filter(type__in=(MESSAGE_COMMENT_POST, MESSAGE_REPLY_COMMENT))
    if kind == 'audit':
        return queryset.filter(type=MESSAGE_AUDIT_REJECTED)
    if kind != 'all':
        raise serializers.ValidationError({
            'type': '只支持 all、like、comment 或 audit',
        })
    return queryset


class MessagesView(AuthenticatedV1APIView):
    def get(self, request):
        profile = self.get_profile()
        queryset = InteractionMessage.objects.filter(recipient=profile).select_related(
            'sender',
            'sender__mini_program_profile',
            'sender__userinformation',
            'target_post',
            'root_post',
            'target_review__course',
        )
        queryset = message_filter(queryset, request.query_params.get('type', 'all'))
        read = request.query_params.get('read', 'all')
        if read not in ('all', 'true', 'false'):
            raise serializers.ValidationError({
                'read': '只支持 all、true 或 false',
            })
        if read in ('true', 'false'):
            queryset = queryset.filter(is_read=(read == 'true'))
        return Response(paginate(request, queryset, serialize_message, ('-id',)))


class UnreadCountView(AuthenticatedV1APIView):
    def get(self, request):
        profile = self.get_profile()
        base = InteractionMessage.objects.filter(recipient=profile, is_read=False)
        like_count = message_filter(base, 'like').count()
        comment_count = message_filter(base, 'comment').count()
        audit_count = message_filter(base, 'audit').count()
        return Response({
            'total': like_count + comment_count + audit_count,
            'like': like_count,
            'comment': comment_count,
            'audit': audit_count,
        })


class MarkMessagesReadView(AuthenticatedV1APIView):
    def post(self, request):
        serializer = MessageReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = self.get_profile()
        queryset = InteractionMessage.objects.filter(
            recipient=profile,
            is_read=False,
            id__lte=serializer.validated_data['maxId'],
        )
        queryset = message_filter(queryset, serializer.validated_data['type'])
        updated = queryset.update(is_read=True)
        return Response({'updatedCount': updated})


class PostsView(IdempotentCreateMixin, PublicV1APIView):
    def get(self, request):
        queryset = public_main_posts()
        sort = request.query_params.get('sort', 'latest')
        ordering = ('-createTime', '-pk')
        if sort == 'hot':
            ordering = (
                '-mini_program_extension__like_count',
                '-mini_program_extension__comment_count',
                '-createTime',
                '-pk',
            )
        elif sort != 'latest':
            raise serializers.ValidationError({'sort': '只支持 latest 或 hot'})
        return Response(paginate(
            request,
            queryset,
            lambda post: serialize_post(post, request),
            ordering,
        ))

    @transaction.atomic
    def post(self, request):
        if not request.user or not request.user.is_authenticated:
            self.permission_denied(request)
        profile = self.get_profile()
        replay = self.replay_idempotent_response(profile)
        if replay:
            return replay

        serializer = CreatePostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        latest = Post.objects.filter(
            createdBy=profile,
            replyToId__isnull=True,
        ).order_by('-createTime').first()
        if latest:
            elapsed = (timezone.now() - latest.createTime).total_seconds()
            if elapsed < 60:
                raise OperationTooFrequent(math.ceil(60 - elapsed))

        image_ids = data['imageIds']
        assets = list(UploadAsset.objects.select_for_update().filter(
            image_id__in=image_ids,
            uploader=profile,
            bound_at__isnull=True,
        ).select_related('image'))
        if len(assets) != len(set(image_ids)):
            raise serializers.ValidationError({
                'imageIds': '图片不存在、已被使用或不属于当前用户',
            })

        audit_status, audit_message = audit_text(
            profile,
            data['content'],
            title=data['title'],
        )
        if any(asset.audit_status != AUDIT_APPROVED for asset in assets):
            if audit_status == AUDIT_APPROVED:
                audit_status = 'PENDING'
                audit_message = '等待图片安全审核'

        post = Post.objects.create(
            tag=None,
            replyToId=None,
            replyToComment=None,
            viewableToGuest=True,
            createdBy=profile,
        )
        content = Content.objects.create(
            post=post,
            title=data['title'],
            text=data['content'],
            editedBy=profile,
        )
        content.images.set([asset.image for asset in assets])
        PostExtension.objects.create(
            post=post,
            section=data['section'],
            is_anonymous=data['isAnonymous'],
            audit_status=audit_status,
            audit_message=audit_message,
        )
        if assets:
            UploadAsset.objects.filter(pk__in=[asset.pk for asset in assets]).update(
                bound_at=timezone.now(),
            )

        response_data = {
            'postId': str(post.pk),
            'auditStatus': audit_status,
            'visible': audit_status == AUDIT_APPROVED,
            'createdAt': milliseconds(post.createTime),
        }
        if audit_status == AUDIT_REJECTED:
            create_audit_rejected_message(profile, target_post=post)
            rejected_data = {
                'businessCode': 10006,
                'message': audit_message,
                'data': {'postId': str(post.pk)},
            }
            self.store_idempotent_response(
                profile,
                rejected_data,
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
            return Response(rejected_data, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.store_idempotent_response(profile, response_data, status.HTTP_201_CREATED)
        return Response(response_data, status=status.HTTP_201_CREATED)


class PostDetailView(PublicV1APIView):
    def get_object(self, post_id):
        post = get_object_or_404(
            Post.objects.select_related(
                'createdBy',
                'createdBy__mini_program_profile',
                'createdBy__userinformation',
                'mini_program_extension',
            ).prefetch_related('contents__images', 'mini_program_likes'),
            pk=parse_post_id(post_id),
            replyToId__isnull=True,
        )
        if is_public_post(post):
            return post
        authenticated = self.request.user and self.request.user.is_authenticated
        if authenticated and post.createdBy_id == self.request.user.pk and not post.deleted:
            return post
        from rest_framework.exceptions import NotFound
        raise NotFound('帖子不存在或已删除')

    def get(self, request, post_id):
        post = self.get_object(post_id)
        return Response(serialize_post(post, request, detail=True))

    @transaction.atomic
    def delete(self, request, post_id):
        if not request.user or not request.user.is_authenticated:
            self.permission_denied(request)
        post = self.get_object(post_id)
        if post.createdBy_id != request.user.pk:
            self.permission_denied(request, message='只能删除自己的帖子')
        profile = self.get_profile()
        post.deleted = True
        post.deletedBy = profile
        post.save(update_fields=['deleted', 'deletedBy'])
        extension = get_extension(post)
        if extension and extension.deleted_at is None:
            extension.deleted_at = timezone.now()
            extension.save(update_fields=['deleted_at'])
        return Response(None)


class CommentsView(IdempotentCreateMixin, PublicV1APIView):
    def get_main_post(self, post_id):
        post = get_object_or_404(
            Post.objects.select_related('createdBy', 'mini_program_extension'),
            pk=parse_post_id(post_id, 'postId'),
            replyToId__isnull=True,
        )
        if not is_public_post(post):
            from rest_framework.exceptions import NotFound
            raise NotFound('帖子不存在或已删除')
        return post

    def get(self, request, post_id):
        post = self.get_main_post(post_id)
        replies = Post.objects.filter(
            deleted=False,
            censored=False,
            mini_program_extension__audit_status=AUDIT_APPROVED,
            mini_program_extension__deleted_at__isnull=True,
        ).select_related(
            'createdBy',
            'createdBy__mini_program_profile',
            'createdBy__userinformation',
            'replyToId__createdBy',
            'replyToId__createdBy__mini_program_profile',
            'replyToId__createdBy__userinformation',
            'mini_program_extension',
        ).prefetch_related('contents', 'mini_program_likes').order_by(
            'createTime', 'pk'
        )
        queryset = Post.objects.filter(
            replyToId=post,
            replyToComment__isnull=True,
            deleted=False,
            censored=False,
            mini_program_extension__audit_status=AUDIT_APPROVED,
            mini_program_extension__deleted_at__isnull=True,
        ).select_related(
            'createdBy',
            'createdBy__mini_program_profile',
            'createdBy__userinformation',
            'replyToId__createdBy',
            'replyToId__createdBy__mini_program_profile',
            'replyToId__createdBy__userinformation',
            'mini_program_extension',
        ).prefetch_related(
            'contents',
            'mini_program_likes',
            Prefetch(
                'post_reply_to_comment',
                queryset=replies,
                to_attr='_public_replies',
            ),
        )
        sort = request.query_params.get('sort', 'latest')
        ordering = ('createTime', 'pk')
        if sort == 'hot':
            ordering = ('-mini_program_extension__like_count', 'createTime', 'pk')
        elif sort != 'latest':
            raise serializers.ValidationError({'sort': '只支持 latest 或 hot'})
        return Response(paginate(
            request,
            queryset,
            lambda comment: serialize_comment(comment, request),
            ordering,
        ))

    @transaction.atomic
    def post(self, request, post_id):
        if not request.user or not request.user.is_authenticated:
            self.permission_denied(request)
        profile = self.get_profile()
        replay = self.replay_idempotent_response(profile)
        if replay:
            return replay
        main_post = self.get_main_post(post_id)
        serializer = CreateCommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        root = None
        target = main_post
        if data.get('rootId'):
            root = get_object_or_404(
                Post.objects.select_related('replyToId', 'createdBy'),
                pk=parse_post_id(data['rootId'], 'rootId'),
                replyToId=main_post,
                replyToComment__isnull=True,
                deleted=False,
                mini_program_extension__audit_status=AUDIT_APPROVED,
                mini_program_extension__deleted_at__isnull=True,
            )
            target = get_object_or_404(
                Post.objects.select_related('createdBy', 'replyToId', 'replyToComment'),
                pk=parse_post_id(data['replyToCommentId'], 'replyToCommentId'),
                deleted=False,
                mini_program_extension__audit_status=AUDIT_APPROVED,
                mini_program_extension__deleted_at__isnull=True,
            )
            if target.pk != root.pk and target.replyToComment_id != root.pk:
                raise serializers.ValidationError({
                    'replyToCommentId': '被回复内容不属于指定一级评论',
                })

        audit_status, audit_message = audit_text(profile, data['content'])
        comment = Post.objects.create(
            tag=None,
            replyToId=target,
            replyToComment=root,
            viewableToGuest=True,
            createdBy=profile,
        )
        Content.objects.create(
            post=comment,
            title=None,
            text=data['content'],
            editedBy=profile,
        )
        PostExtension.objects.create(
            post=comment,
            section=SECTION_CONFESSION_WALL,
            audit_status=audit_status,
            audit_message=audit_message,
        )
        if audit_status == AUDIT_APPROVED:
            main_extension = PostExtension.objects.select_for_update().get(post=main_post)
            main_extension.comment_count = Post.objects.filter(
                Q(replyToId=main_post, replyToComment__isnull=True)
                | Q(replyToComment__replyToId=main_post),
                deleted=False,
                censored=False,
                mini_program_extension__audit_status=AUDIT_APPROVED,
                mini_program_extension__deleted_at__isnull=True,
            ).count()
            main_extension.save(update_fields=['comment_count'])
            create_comment_message(comment)

        response_data = {
            'commentId': str(comment.pk),
            'auditStatus': audit_status,
            'visible': audit_status == AUDIT_APPROVED,
            'createdAt': milliseconds(comment.createTime),
        }
        if audit_status == AUDIT_REJECTED:
            create_audit_rejected_message(profile, target_post=comment)
            rejected_data = {
                'businessCode': 10006,
                'message': audit_message,
                'data': {'commentId': str(comment.pk)},
            }
            self.store_idempotent_response(
                profile,
                rejected_data,
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
            return Response(rejected_data, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.store_idempotent_response(profile, response_data, status.HTTP_201_CREATED)
        return Response(response_data, status=status.HTTP_201_CREATED)


class RepliesView(PublicV1APIView):
    def get(self, request, comment_id):
        root = get_object_or_404(
            Post.objects.select_related('replyToId__createdBy'),
            pk=parse_post_id(comment_id, 'commentId'),
            replyToId__isnull=False,
            replyToComment__isnull=True,
            deleted=False,
            mini_program_extension__audit_status=AUDIT_APPROVED,
            mini_program_extension__deleted_at__isnull=True,
        )
        main_post = root.replyToId
        if not is_public_post(main_post):
            from rest_framework.exceptions import NotFound
            raise NotFound('帖子不存在或已删除')
        queryset = Post.objects.filter(
            replyToComment=root,
            deleted=False,
            censored=False,
            mini_program_extension__audit_status=AUDIT_APPROVED,
            mini_program_extension__deleted_at__isnull=True,
        ).select_related(
            'createdBy',
            'createdBy__mini_program_profile',
            'createdBy__userinformation',
            'replyToId__createdBy',
            'replyToId__createdBy__mini_program_profile',
            'replyToId__createdBy__userinformation',
            'mini_program_extension',
        ).prefetch_related('contents', 'mini_program_likes')
        return Response(paginate(
            request,
            queryset,
            lambda reply: serialize_reply(reply, request, main_post),
            ('createTime', 'pk'),
        ))


class CommentDetailView(AuthenticatedV1APIView):
    @transaction.atomic
    def delete(self, request, comment_id):
        comment = get_object_or_404(
            Post.objects.select_related(
                'replyToId',
                'replyToComment__replyToId',
                'mini_program_extension',
            ),
            pk=parse_post_id(comment_id, 'commentId'),
            replyToId__isnull=False,
            deleted=False,
        )
        main = root_post(comment)
        if request.user.pk not in (comment.createdBy_id, main.createdBy_id):
            self.permission_denied(request, message='无权删除该评论')
        profile = self.get_profile()
        kind = post_kind(comment)
        hidden_count = 1
        if kind == 'comment':
            hidden_count += Post.objects.filter(
                replyToComment=comment,
                deleted=False,
                censored=False,
                mini_program_extension__audit_status=AUDIT_APPROVED,
                mini_program_extension__deleted_at__isnull=True,
            ).count()
        comment.deleted = True
        comment.deletedBy = profile
        comment.save(update_fields=['deleted', 'deletedBy'])
        extension = get_extension(comment)
        was_approved = extension and extension.audit_status == AUDIT_APPROVED
        if extension and extension.deleted_at is None:
            extension.deleted_at = timezone.now()
            extension.save(update_fields=['deleted_at'])
        if was_approved:
            main_extension = PostExtension.objects.select_for_update().get(post=main)
            main_extension.comment_count = max(
                0,
                main_extension.comment_count - hidden_count,
            )
            main_extension.save(update_fields=['comment_count'])
        return Response(None)


class LikeToggleView(AuthenticatedV1APIView):
    @transaction.atomic
    def post(self, request):
        serializer = LikeToggleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        profile = self.get_profile()
        desired = data.get('liked')

        if data['targetType'] in (LIKE_POST, LIKE_COMMENT):
            target = get_object_or_404(
                Post.objects.select_related('createdBy', 'mini_program_extension'),
                pk=parse_post_id(data['targetId'], 'targetId'),
            )
            expected_kind = 'post' if data['targetType'] == LIKE_POST else None
            if expected_kind and post_kind(target) != expected_kind:
                raise serializers.ValidationError({'targetType': '目标不是帖子'})
            if data['targetType'] == LIKE_COMMENT and post_kind(target) == 'post':
                raise serializers.ValidationError({'targetType': '目标不是评论'})
            if not is_public_post(target):
                from rest_framework.exceptions import NotFound
                raise NotFound('点赞目标不存在或不可见')
            if not is_public_post(root_post(target)):
                from rest_framework.exceptions import NotFound
                raise NotFound('点赞目标所属帖子不存在或不可见')
            extension = PostExtension.objects.select_for_update().get(post=target)
            existing = PostLike.objects.filter(user=profile, post=target).first()
            should_like = (not bool(existing)) if desired is None else bool(desired)
            created = False
            if should_like and not existing:
                PostLike.objects.create(user=profile, post=target)
                created = True
            elif not should_like and existing:
                existing.delete()
            extension.like_count = PostLike.objects.filter(post=target).count()
            extension.save(update_fields=['like_count'])
            if created:
                create_like_message(profile, target_post=target)
            return Response({
                'liked': should_like,
                'likeCount': extension.like_count,
            })

        review = get_object_or_404(
            CourseReview.objects.select_related('user', 'course'),
            pk=parse_uuid(data['targetId'], 'targetId'),
            deleted_at__isnull=True,
            audit_status=AUDIT_APPROVED,
            course__deleted_at__isnull=True,
        )
        review = CourseReview.objects.select_for_update().get(pk=review.pk)
        existing = CourseReviewLike.objects.filter(user=profile, review=review).first()
        should_like = (not bool(existing)) if desired is None else bool(desired)
        created = False
        if should_like and not existing:
            CourseReviewLike.objects.create(user=profile, review=review)
            created = True
        elif not should_like and existing:
            existing.delete()
        review.like_count = CourseReviewLike.objects.filter(review=review).count()
        review.save(update_fields=['like_count'])
        if created:
            create_like_message(profile, target_review=review)
        return Response({'liked': should_like, 'likeCount': review.like_count})


def serialize_course(course):
    return {
        'courseId': str(course.pk),
        'name': course.name,
        'code': course.code,
        'teacher': course.teacher,
        'college': course.college,
        'credit': str(course.credit),
        'ratingAvg': str(course.rating_average),
        'reviewCount': course.review_count,
    }


class CoursesView(IdempotentCreateMixin, PublicV1APIView):
    def get(self, request):
        queryset = Course.objects.filter(deleted_at__isnull=True)
        keyword = (request.query_params.get('keyword') or '').strip()
        if keyword:
            queryset = queryset.filter(
                Q(name__icontains=keyword)
                | Q(code__icontains=keyword)
                | Q(teacher__icontains=keyword)
            )
        sort = request.query_params.get('sort', 'hot')
        ordering = ('-review_count', '-rating_average', '-created_at', '-id')
        if sort == 'rating':
            ordering = ('-rating_average', '-review_count', '-created_at', '-id')
        elif sort == 'latest':
            ordering = ('-created_at', '-id')
        elif sort != 'hot':
            raise serializers.ValidationError({'sort': '只支持 hot、rating 或 latest'})
        return Response(paginate(request, queryset, serialize_course, ordering))

    @transaction.atomic
    def post(self, request):
        if not request.user or not request.user.is_authenticated:
            self.permission_denied(request)
        profile = self.get_profile()
        replay = self.replay_idempotent_response(profile)
        if replay:
            return replay
        serializer = CreateCourseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)
        normalized_name = data.pop('_normalized_name')
        normalized_teacher = data.pop('_normalized_teacher')
        existing = Course.objects.filter(
            normalized_name=normalized_name,
            normalized_teacher=normalized_teacher,
        ).first()
        if existing:
            raise DuplicateOperation(
                '课程已存在',
                data={
                    'courseId': str(existing.pk),
                    'name': existing.name,
                    'teacher': existing.teacher,
                },
            )
        try:
            with transaction.atomic():
                course = Course.objects.create(
                    name=data['name'],
                    code=data['code'],
                    teacher=data['teacher'],
                    college=data['college'],
                    credit=data['credit'],
                    created_by=profile,
                )
        except IntegrityError:
            existing = Course.objects.get(
                normalized_name=normalized_name,
                normalized_teacher=normalized_teacher,
            )
            raise DuplicateOperation(
                '课程已存在',
                data={'courseId': str(existing.pk)},
            )
        response_data = {'courseId': str(course.pk)}
        self.store_idempotent_response(profile, response_data, status.HTTP_201_CREATED)
        return Response(response_data, status=status.HTTP_201_CREATED)


class CourseDetailView(PublicV1APIView):
    def get(self, request, course_id):
        course = get_object_or_404(Course, pk=course_id, deleted_at__isnull=True)
        data = serialize_course(course)
        authenticated = request.user and request.user.is_authenticated
        my_review = None
        if authenticated:
            my_review = CourseReview.objects.filter(
                course=course,
                user_id=request.user.pk,
                deleted_at__isnull=True,
            ).first()
        data.update({
            'ratingDistribution': rating_distribution(course),
            'myReviewId': str(my_review.pk) if my_review else None,
        })
        return Response(data)


class CourseReviewsView(IdempotentCreateMixin, PublicV1APIView):
    def get_course(self, course_id):
        return get_object_or_404(Course, pk=course_id, deleted_at__isnull=True)

    def get(self, request, course_id):
        course = self.get_course(course_id)
        queryset = public_reviews(course)
        sort = request.query_params.get('sort', 'latest')
        ordering = ('-created_at', '-id')
        if sort == 'hot':
            ordering = ('-like_count', '-created_at', '-id')
        elif sort != 'latest':
            raise serializers.ValidationError({'sort': '只支持 latest 或 hot'})
        return Response(paginate(
            request,
            queryset,
            lambda review: serialize_review(review, request),
            ordering,
        ))

    @transaction.atomic
    def post(self, request, course_id):
        if not request.user or not request.user.is_authenticated:
            self.permission_denied(request)
        profile = self.get_profile()
        replay = self.replay_idempotent_response(profile)
        if replay:
            return replay
        course = self.get_course(course_id)
        serializer = ReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        existing = CourseReview.objects.filter(course=course, user=profile).first()
        if existing and existing.deleted_at is None:
            raise DuplicateOperation(
                '你已经评价过该课程',
                data={'reviewId': str(existing.pk)},
            )
        audit_status, audit_message = audit_text(profile, data['content'])
        if existing:
            review = existing
            review.rating = data['rating']
            review.content = data['content']
            review.is_anonymous = data['isAnonymous']
            review.audit_status = audit_status
            review.audit_message = audit_message
            review.deleted_at = None
            review.save()
        else:
            review = CourseReview.objects.create(
                course=course,
                user=profile,
                rating=data['rating'],
                content=data['content'],
                is_anonymous=data['isAnonymous'],
                audit_status=audit_status,
                audit_message=audit_message,
            )
        recalculate_course(course.pk)
        response_data = {
            'reviewId': str(review.pk),
            'auditStatus': audit_status,
            'visible': audit_status == AUDIT_APPROVED,
            'createdAt': milliseconds(review.created_at),
        }
        if audit_status == AUDIT_REJECTED:
            create_audit_rejected_message(profile, target_review=review)
            rejected_data = {
                'businessCode': 10006,
                'message': audit_message,
                'data': {'reviewId': str(review.pk)},
            }
            self.store_idempotent_response(
                profile,
                rejected_data,
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
            return Response(rejected_data, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.store_idempotent_response(profile, response_data, status.HTTP_201_CREATED)
        return Response(response_data, status=status.HTTP_201_CREATED)


class ReviewDetailView(AuthenticatedV1APIView):
    def get_object(self, review_id):
        review = get_object_or_404(
            CourseReview.objects.select_related('course', 'user'),
            pk=review_id,
            deleted_at__isnull=True,
        )
        if review.user_id != self.request.user.pk:
            self.permission_denied(self.request, message='只能修改或删除自己的评价')
        return review

    @transaction.atomic
    def put(self, request, review_id):
        review = self.get_object(review_id)
        serializer = ReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        profile = self.get_profile()
        audit_status, audit_message = audit_text(profile, data['content'])
        review.rating = data['rating']
        review.content = data['content']
        review.is_anonymous = data['isAnonymous']
        review.audit_status = audit_status
        review.audit_message = audit_message
        review.save()
        recalculate_course(review.course_id)
        response_data = {
            'reviewId': str(review.pk),
            'auditStatus': audit_status,
            'updatedAt': milliseconds(review.updated_at),
        }
        if audit_status == AUDIT_REJECTED:
            create_audit_rejected_message(profile, target_review=review)
            return Response({
                'businessCode': 10006,
                'message': audit_message,
                'data': response_data,
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        return Response(response_data)

    @transaction.atomic
    def delete(self, request, review_id):
        review = self.get_object(review_id)
        review.deleted_at = timezone.now()
        review.save(update_fields=['deleted_at', 'updated_at'])
        recalculate_course(review.course_id)
        return Response(None)
