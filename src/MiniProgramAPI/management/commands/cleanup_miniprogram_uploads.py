from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from MiniProgramAPI.models import UploadAsset


class Command(BaseCommand):
    help = 'Delete old unbound MiniProgramAPI upload records and their PostImage rows.'

    def add_arguments(self, parser):
        parser.add_argument('--older-than-hours', type=int, default=24)
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **options):
        hours = options['older_than_hours']
        if hours < 1:
            raise CommandError('--older-than-hours must be at least 1')
        cutoff = timezone.now() - timedelta(hours=hours)
        queryset = UploadAsset.objects.filter(
            bound_at__isnull=True,
            created_at__lt=cutoff,
        )
        count = queryset.count()
        if options['dry_run']:
            self.stdout.write('Would delete {} unbound upload(s).'.format(count))
            return

        with transaction.atomic():
            image_ids = list(queryset.values_list('image_id', flat=True))
            queryset.delete()
            # UploadAsset is the ownership record. Delete only images that were
            # still unbound and selected above; never scan unrelated media.
            from CommunityAPI.models import PostImage
            PostImage.objects.filter(pk__in=image_ids).delete()
        self.stdout.write(self.style.SUCCESS(
            'Deleted {} unbound upload(s).'.format(count)
        ))
