from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from CommunityAPI.models import Post
from MiniProgramAPI.constants import AUDIT_APPROVED
from MiniProgramAPI.models import Course, PostExtension, PostLike
from MiniProgramAPI.services import recalculate_course


class Command(BaseCommand):
    help = 'Rebuild cached like/comment/course rating counters for MiniProgramAPI.'

    def handle(self, *args, **options):
        rebuilt_posts = 0
        for extension in PostExtension.objects.select_related('post').iterator():
            with transaction.atomic():
                extension = PostExtension.objects.select_for_update().get(pk=extension.pk)
                extension.like_count = PostLike.objects.filter(post_id=extension.post_id).count()
                if extension.post.replyToId_id is None:
                    extension.comment_count = Post.objects.filter(
                        Q(replyToId_id=extension.post_id, replyToComment__isnull=True)
                        | Q(replyToComment__replyToId_id=extension.post_id),
                        deleted=False,
                        censored=False,
                        mini_program_extension__audit_status=AUDIT_APPROVED,
                        mini_program_extension__deleted_at__isnull=True,
                    ).count()
                extension.save(update_fields=['like_count', 'comment_count'])
            rebuilt_posts += 1

        rebuilt_courses = 0
        for course_id in Course.objects.values_list('pk', flat=True).iterator():
            recalculate_course(course_id)
            rebuilt_courses += 1

        self.stdout.write(self.style.SUCCESS(
            'Rebuilt {} post counters and {} course counters.'.format(
                rebuilt_posts,
                rebuilt_courses,
            )
        ))
