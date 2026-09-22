import hashlib
import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from CommunityAPI.models import Post, PostImage
from UserAuthAPI.models import UserProfile

from .constants import AUDIT_PENDING, AUDIT_STATUS_CHOICES, MESSAGE_TYPE_CHOICES


class MiniProgramProfile(models.Model):
    user = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='mini_program_profile',
    )
    nickname = models.CharField(max_length=30, blank=True, default='')
    avatar_url = models.URLField(blank=True, default='')
    college = models.CharField(max_length=150, blank=True, default='')
    wechat_openid = models.CharField(
        max_length=128,
        unique=True,
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(auto_now=True)


class PostExtension(models.Model):
    post = models.OneToOneField(
        Post,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='mini_program_extension',
    )
    section = models.PositiveSmallIntegerField(default=1, db_index=True)
    is_anonymous = models.BooleanField(default=False)
    audit_status = models.CharField(
        max_length=16,
        choices=AUDIT_STATUS_CHOICES,
        default=AUDIT_PENDING,
        db_index=True,
    )
    audit_message = models.CharField(max_length=500, blank=True, default='')
    like_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(
                fields=['section', 'audit_status', 'deleted_at'],
                name='mini_post_public_idx',
            ),
        ]


class PostLike(models.Model):
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='mini_program_post_likes',
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='mini_program_likes',
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'post'],
                name='mini_unique_user_post_like',
            ),
        ]


class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    normalized_name = models.CharField(max_length=150, editable=False)
    code = models.CharField(max_length=50, blank=True, default='')
    teacher = models.CharField(max_length=100)
    normalized_teacher = models.CharField(max_length=100, editable=False)
    college = models.CharField(max_length=150)
    credit = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    dedupe_key = models.CharField(max_length=64, unique=True, editable=False)
    rating_sum = models.PositiveIntegerField(default=0)
    rating_average = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    review_count = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(
        UserProfile,
        null=True,
        on_delete=models.SET_NULL,
        related_name='mini_program_created_courses',
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['normalized_name'], name='mini_course_name_idx'),
            models.Index(fields=['normalized_teacher'], name='mini_course_teacher_idx'),
            models.Index(fields=['-review_count', '-rating_average'], name='mini_course_hot_idx'),
        ]

    @staticmethod
    def normalize(value):
        return ' '.join((value or '').casefold().split())

    def save(self, *args, **kwargs):
        self.normalized_name = self.normalize(self.name)
        self.normalized_teacher = self.normalize(self.teacher)
        raw_key = '{}\x00{}'.format(self.normalized_name, self.normalized_teacher)
        self.dedupe_key = hashlib.sha256(raw_key.encode('utf-8')).hexdigest()
        super().save(*args, **kwargs)


class CourseReview(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='mini_program_course_reviews',
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    content = models.CharField(max_length=500)
    is_anonymous = models.BooleanField(default=False)
    audit_status = models.CharField(
        max_length=16,
        choices=AUDIT_STATUS_CHOICES,
        default=AUDIT_PENDING,
        db_index=True,
    )
    audit_message = models.CharField(max_length=500, blank=True, default='')
    like_count = models.PositiveIntegerField(default=0)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['course', 'user'],
                name='mini_unique_user_course_review',
            ),
        ]


class CourseReviewLike(models.Model):
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='mini_program_review_likes',
    )
    review = models.ForeignKey(
        CourseReview,
        on_delete=models.CASCADE,
        related_name='likes',
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'review'],
                name='mini_unique_user_review_like',
            ),
        ]


class InteractionMessage(models.Model):
    recipient = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='mini_program_messages',
    )
    sender = models.ForeignKey(
        UserProfile,
        null=True,
        on_delete=models.SET_NULL,
        related_name='mini_program_sent_messages',
    )
    type = models.CharField(max_length=32, choices=MESSAGE_TYPE_CHOICES)
    target_post = models.ForeignKey(
        Post,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='mini_program_messages',
    )
    root_post = models.ForeignKey(
        Post,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='mini_program_root_messages',
    )
    target_review = models.ForeignKey(
        CourseReview,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='messages',
    )
    snippet = models.CharField(max_length=120, blank=True, default='')
    cover = models.URLField(blank=True, default='')
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(
                fields=['recipient', 'is_read', '-id'],
                name='mini_message_unread_idx',
            ),
        ]


class UploadAsset(models.Model):
    image = models.OneToOneField(
        PostImage,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='mini_program_upload',
    )
    uploader = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='mini_program_uploads',
    )
    object_key = models.CharField(max_length=500, unique=True)
    content_type = models.CharField(max_length=100)
    size = models.PositiveIntegerField()
    audit_status = models.CharField(
        max_length=16,
        choices=AUDIT_STATUS_CHOICES,
        default=AUDIT_PENDING,
    )
    bound_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class IdempotencyRecord(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    key = models.CharField(max_length=128)
    method = models.CharField(max_length=10)
    path = models.CharField(max_length=500)
    response_status = models.PositiveSmallIntegerField(default=200)
    response_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'key', 'method', 'path'],
                name='mini_unique_idempotency_key',
            ),
        ]
