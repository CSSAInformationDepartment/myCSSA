from decimal import Decimal

from rest_framework import serializers

from .constants import LIKE_COMMENT, LIKE_POST, LIKE_REVIEW, SECTION_CONFESSION_WALL
from .models import Course


class WechatBindSerializer(serializers.Serializer):
    code = serializers.CharField(min_length=1, max_length=128, trim_whitespace=True)


class UploadTokenSerializer(serializers.Serializer):
    filename = serializers.CharField(max_length=255)
    contentType = serializers.ChoiceField(
        choices=('image/jpeg', 'image/png', 'image/webp'),
    )
    size = serializers.IntegerField(min_value=1, max_value=10 * 1024 * 1024)


class UploadCompleteSerializer(serializers.Serializer):
    objectKey = serializers.CharField(max_length=500)
    contentType = serializers.ChoiceField(
        choices=('image/jpeg', 'image/png', 'image/webp'),
    )
    size = serializers.IntegerField(min_value=1, max_value=10 * 1024 * 1024)


class CreatePostSerializer(serializers.Serializer):
    section = serializers.IntegerField(default=SECTION_CONFESSION_WALL)
    title = serializers.CharField(min_length=1, max_length=30, trim_whitespace=True)
    content = serializers.CharField(min_length=1, max_length=2000, trim_whitespace=True)
    imageIds = serializers.ListField(
        child=serializers.UUIDField(),
        max_length=9,
        required=False,
        default=list,
    )
    isAnonymous = serializers.BooleanField(default=False)

    def validate_section(self, value):
        if value != SECTION_CONFESSION_WALL:
            raise serializers.ValidationError('暂不支持该板块')
        return value


class CreateCommentSerializer(serializers.Serializer):
    content = serializers.CharField(min_length=1, max_length=500, trim_whitespace=True)
    rootId = serializers.CharField(allow_null=True, required=False, default=None)
    replyToCommentId = serializers.CharField(allow_null=True, required=False, default=None)

    def validate(self, attrs):
        root_id = attrs.get('rootId')
        reply_id = attrs.get('replyToCommentId')
        if bool(root_id) != bool(reply_id):
            raise serializers.ValidationError(
                'rootId 和 replyToCommentId 必须同时为空或同时提供'
            )
        return attrs


class LikeToggleSerializer(serializers.Serializer):
    targetType = serializers.ChoiceField(
        choices=(LIKE_POST, LIKE_COMMENT, LIKE_REVIEW),
    )
    targetId = serializers.CharField(max_length=64)
    liked = serializers.BooleanField(required=False)


class MessageReadSerializer(serializers.Serializer):
    type = serializers.ChoiceField(
        choices=('all', 'like', 'comment', 'audit'),
        default='all',
    )
    maxId = serializers.IntegerField(min_value=1)


class CreateCourseSerializer(serializers.Serializer):
    name = serializers.CharField(min_length=1, max_length=150, trim_whitespace=True)
    code = serializers.CharField(max_length=50, required=False, allow_blank=True, default='')
    teacher = serializers.CharField(min_length=1, max_length=100, trim_whitespace=True)
    college = serializers.CharField(min_length=1, max_length=150, trim_whitespace=True)
    credit = serializers.DecimalField(max_digits=6, decimal_places=2, min_value=Decimal('0'))

    def validate(self, attrs):
        normalized_name = Course.normalize(attrs['name'])
        normalized_teacher = Course.normalize(attrs['teacher'])
        attrs['_normalized_name'] = normalized_name
        attrs['_normalized_teacher'] = normalized_teacher
        return attrs


class ReviewSerializer(serializers.Serializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)
    content = serializers.CharField(min_length=1, max_length=500, trim_whitespace=True)
    isAnonymous = serializers.BooleanField(default=False)
