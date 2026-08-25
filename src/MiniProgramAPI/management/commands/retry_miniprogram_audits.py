from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from CommunityAPI.models import Post
from MiniProgramAPI.constants import AUDIT_APPROVED, AUDIT_PENDING, AUDIT_REJECTED
from MiniProgramAPI.models import CourseReview, PostExtension
from MiniProgramAPI.services import (
    audit_text,
    create_audit_rejected_message,
    create_comment_message,
    current_content,
    post_kind,
    recalculate_course,
    root_post,
)


class Command(BaseCommand):
    help = 'Retry pending text audits. Safe to run periodically; pending failures remain pending.'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=100)

    def handle(self, *args, **options):
        limit = options['limit']
        if limit < 1 or limit > 1000:
            raise ValueError('--limit must be between 1 and 1000')

        processed = 0
        post_ids = list(PostExtension.objects.filter(
            audit_status=AUDIT_PENDING,
            deleted_at__isnull=True,
            post__deleted=False,
        ).values_list('post_id', flat=True)[:limit])
        for post_id in post_ids:
            with transaction.atomic():
                extension = PostExtension.objects.select_for_update().select_related(
                    'post__createdBy',
                ).get(post_id=post_id)
                if extension.audit_status != AUDIT_PENDING:
                    continue
                content = current_content(extension.post)
                audit_status, message = audit_text(
                    extension.post.createdBy,
                    content.text if content else '',
                    title=content.title if content else None,
                )
                if audit_status == AUDIT_PENDING:
                    continue
                extension.audit_status = audit_status
                extension.audit_message = message
                extension.save(update_fields=['audit_status', 'audit_message'])
                if audit_status == AUDIT_REJECTED:
                    create_audit_rejected_message(
                        extension.post.createdBy,
                        target_post=extension.post,
                    )
                elif post_kind(extension.post) != 'post':
                    main = root_post(extension.post)
                    main_extension = PostExtension.objects.select_for_update().get(post=main)
                    main_extension.comment_count = Post.objects.filter(
                        Q(replyToId=main, replyToComment__isnull=True)
                        | Q(replyToComment__replyToId=main),
                        deleted=False,
                        censored=False,
                        mini_program_extension__audit_status=AUDIT_APPROVED,
                        mini_program_extension__deleted_at__isnull=True,
                    ).count()
                    main_extension.save(update_fields=['comment_count'])
                    create_comment_message(extension.post)
                processed += 1

        remaining = max(0, limit - processed)
        review_ids = list(CourseReview.objects.filter(
            audit_status=AUDIT_PENDING,
            deleted_at__isnull=True,
        ).values_list('pk', flat=True)[:remaining])
        for review_id in review_ids:
            with transaction.atomic():
                review = CourseReview.objects.select_for_update().select_related(
                    'user', 'course',
                ).get(pk=review_id)
                if review.audit_status != AUDIT_PENDING:
                    continue
                audit_status, message = audit_text(review.user, review.content)
                if audit_status == AUDIT_PENDING:
                    continue
                review.audit_status = audit_status
                review.audit_message = message
                review.save(update_fields=['audit_status', 'audit_message', 'updated_at'])
                recalculate_course(review.course_id)
                if audit_status == AUDIT_REJECTED:
                    create_audit_rejected_message(
                        review.user,
                        target_review=review,
                    )
                processed += 1

        self.stdout.write(self.style.SUCCESS(
            'Resolved {} pending audit(s).'.format(processed)
        ))
