from django.db import migrations
from django.db.models import Q
from django.utils import timezone


def import_legacy_data(apps, schema_editor):
    Post = apps.get_model('CommunityAPI', 'Post')
    FavouritePost = apps.get_model('CommunityAPI', 'FavouritePost')
    PostExtension = apps.get_model('MiniProgramAPI', 'PostExtension')
    PostLike = apps.get_model('MiniProgramAPI', 'PostLike')

    now = timezone.now()
    extensions = []
    for post in Post.objects.all().iterator():
        audit_status = 'REJECTED' if post.censored else 'APPROVED'
        extensions.append(PostExtension(
            post_id=post.pk,
            section=1,
            is_anonymous=False,
            audit_status=audit_status,
            audit_message='历史内容已被管理员屏蔽' if post.censored else '',
            deleted_at=now if post.deleted else None,
        ))
    PostExtension.objects.bulk_create(extensions, ignore_conflicts=True)

    likes = []
    for favourite in FavouritePost.objects.all().iterator():
        likes.append(PostLike(
            user_id=favourite.user_id,
            post_id=favourite.post_id,
        ))
    PostLike.objects.bulk_create(likes, ignore_conflicts=True)

    for extension in PostExtension.objects.select_related('post').all().iterator():
        post = extension.post
        extension.like_count = PostLike.objects.filter(post_id=post.pk).count()
        if post.replyToId_id is None:
            extension.comment_count = Post.objects.filter(
                Q(replyToId_id=post.pk, replyToComment__isnull=True)
                | Q(replyToComment__replyToId_id=post.pk),
                deleted=False,
                censored=False,
            ).count()
        extension.save(update_fields=['like_count', 'comment_count'])


class Migration(migrations.Migration):

    dependencies = [
        ('MiniProgramAPI', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(import_legacy_data, migrations.RunPython.noop),
    ]
