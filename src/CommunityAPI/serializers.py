from typing import Optional
from django.contrib import postgres
from django.contrib.postgres import fields
from rest_framework.serializers import ValidationError
from rest_framework import serializers
from django.db.transaction import atomic
from rest_framework.views import APIView
from drf_yasg.utils import swagger_serializer_method
from sorl.thumbnail import get_thumbnail

from UserAuthAPI.models import UserProfile

from . import models

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tag
        fields = ['id', 'title']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Notification
        fields = ['id', 'targetPost','data', 'type', 'read']

        
class PostImageSerializer(serializers.ModelSerializer):

    url = serializers.SerializerMethodField('getImageUrl', label='原图的url')
    thumbnail = serializers.SerializerMethodField('getThumbnail', label='缩略图（显示在图片列表里）的url，大小为 50x50')
    small = serializers.SerializerMethodField('getSmall', label='压缩图的url，最大为 300x300')

    class Meta:
        model = models.PostImage
        fields = ['id', 'url', 'thumbnail', 'small']

    def _buildAbsoluteUrl(self, image):
        request = self.context['request']
        return request.build_absolute_uri(image.url)

    @swagger_serializer_method(serializer_or_field=serializers.URLField)
    def getImageUrl(self, instance: models.PostImage):
        return self._buildAbsoluteUrl(instance.image)

    @swagger_serializer_method(serializer_or_field=serializers.URLField)
    def getThumbnail(self, instance):
        image = get_thumbnail(instance.image, '50x50', crop='center', quality=99)
        return self._buildAbsoluteUrl(image)

    @swagger_serializer_method(serializer_or_field=serializers.URLField)
    def getSmall(self, instance):
        image = get_thumbnail(instance.image, '300x300', crop='noop', quality=99)
        return self._buildAbsoluteUrl(image)

class ReadContentSerializer(serializers.ModelSerializer):
    images = PostImageSerializer(many=True, read_only=True)

    class Meta:
        model = models.Content
        fields = ['title', 'text', 'editedTime', 'images']


class EditContentSerializer(serializers.ModelSerializer):

    TEXT_LENGTH_MIN=1
    TITLE_LENGTH_MIN=1
    IMAGE_MAX_LENGTH=3

    images = serializers.ListField(write_only=True, max_length=IMAGE_MAX_LENGTH,
        child=serializers.UUIDField(label='图片的UUID列表，想要增删图片，修改这个列表即可。'))

    class Meta:
        model = models.Content
        fields = ['title', 'text', 'images']

    def validate(self, attrs: dict):
        title = attrs.get('title')
        if self.context['view'].basename == 'post':
            if not title:
                raise ValidationError({'title': '主贴必须有标题'})
            elif len(title) < self.TITLE_LENGTH_MIN:
                raise ValidationError({'title': f'主贴标题长度必须大于等于 {self.TITLE_LENGTH_MIN}'})
        else:
            if title != None:
                raise ValidationError({'title': '回复不能有标题'})

        text = attrs.get('text', None)
        if text == None or len(text) < self.TEXT_LENGTH_MIN:
            raise ValidationError({'text': f'帖子正文长度必须大于等于 {self.TEXT_LENGTH_MIN}'})

        return super().validate(attrs)

def resolve_username(profile: UserProfile) -> str:
    info = models.UserInformation.objects.filter(user_id=profile.pk).first()
    if info:
        return info.username
    else:
        # 用用户的全名来当作用户名
        return profile.firstNameEN + ' ' + profile.lastNameEN

def resolve_avatar(profile: UserProfile) -> Optional[str]:
    info = models.UserInformation.objects.filter(user_id=profile.pk).first()
    if info:
        return info.avatarUrl
    elif profile.avatar:
        return profile.avatar.url
    else:
        return None

def resolve_post_content(post: models.Post) -> models.Content:
    content = models.Content.objects.filter(post=post).order_by('-editedTime').first()
    assert content, '一个Post必定有一个Content'
    return content

class PostSerializerMixin:
    """
    提供一些主贴和评论都会用到的公共方法
    """

    def fill_representation(self, repr, instance: models.Post):
        """
        向返回的json填充以下数据：
        帖子正文
        发帖的用户名
        """

        contentModel = resolve_post_content(instance)
        repr['content'] = self.fields['content'].to_representation(contentModel)

        repr['createdBy'] = resolve_username(instance.createdBy)
        repr['creatorAvatar'] = resolve_avatar(instance.createdBy)

    def create_content(self, validated_data, post: models.Post):
        """
        从输入的json创建一个新的content版本
        """

        userProfile: UserProfile = self.context['request'].user

        content = validated_data['content']
        images = content.pop('images')

        contentModel: models.Content = models.Content.objects.create(
            post=post,
            editedBy_id=userProfile.pk,
            **content
        )
        contentModel.images.set(images)
        return contentModel

class ReadMainPostSerializer(PostSerializerMixin, serializers.ModelSerializer):
    """
    只用来处理主贴的读取
    """

    SUMMARY_TEXT_LENGTH = 50 # 25个汉字

    content = ReadContentSerializer(read_only=True)

    createdBy = serializers.CharField(label='创建者的用户名')
    creatorAvatar = serializers.URLField(label='创建者的头像', read_only=True, allow_null=True)

    favouriteCount = serializers.SerializerMethodField(label='收藏该帖子的人的数量')
    isFavourite = serializers.SerializerMethodField(label='本人是否已收藏，如果用户未登录，这里也是false')

    class Meta:
        model = models.Post
        fields = ['id', 'tag', 'createTime', 'viewCount', 'viewableToGuest',
            # 正常情况下我们不需要再声明下面两个field，但是不这么搞的话 drf_yasg 会报错
            'content', 'createdBy', 'creatorAvatar', 'favouriteCount', 'isFavourite']

    def get_favouriteCount(self, instance) -> int:
        return models.FavouritePost.objects.filter(post=instance).count()

    def get_isFavourite(self, instance) -> bool:
        user = self.context['request'].user
        return False if user.is_anonymous else \
            models.FavouritePost.objects.filter(post=instance, user_id=user.id).exists()

    def to_representation(self, instance: models.Post):
        repr = super().to_representation(instance)
        self.fill_representation(repr, instance)

        # 如果是读取文章列表，只保留正文的前25个汉字
        if not self.context['view'].detail:
            repr['content']['text'] = repr['content']['text'][:self.SUMMARY_TEXT_LENGTH]

        return repr

class EditMainPostSerializer(PostSerializerMixin, serializers.ModelSerializer):
    """
    处理主贴的添加和修改。
    """
    content = EditContentSerializer()

    class Meta:
        model = models.Post
        fields = ['tag', 'viewableToGuest',
            # 正常情况下我们不需要再声明下面的field，但是不这么搞的话 drf_yasg 会报错
            'content']

    @atomic
    def create(self, validated_data):

        userProfile: UserProfile = self.context['request'].user

        post = models.Post.objects.create(
            createdBy_id=userProfile.pk,
            tag=validated_data['tag'],
            viewableToGuest=validated_data['viewableToGuest']
        )

        self.create_content(validated_data, post)

        return post

    def update(self, instance, validated_data):

        # TODO: update tag and viewable to guest?

        self.create_content(validated_data, instance)

        return instance

class ReadCommentSerializer(PostSerializerMixin, serializers.ModelSerializer):
    """
    处理一级评论的读取
    """

    content = ReadContentSerializer(read_only=True)

    createdBy = serializers.CharField(label='创建者的用户名')
    creatorAvatar = serializers.URLField(label='创建者的头像', read_only=True, allow_null=True)

    class Meta:
        model = models.Post
        fields = ['id', 'createTime',
            # 正常情况下我们不需要再声明下面两个field，但是不这么搞的话 drf_yasg 会报错
            'content', 'createdBy', 'creatorAvatar',]

    def to_representation(self, instance: models.Post):
        repr = super().to_representation(instance)
        self.fill_representation(repr, instance)
        return repr

def get_post_by_id(id: int) -> models.Post:
    """
    根据id获取一个帖子或评论对象，并确保其没有被屏蔽或删除。
    如果对象不合法，将抛出 ValidationError
    """
    mainPost: models.Post = models.Post.objects.filter(pk=id).first()
    if not mainPost or mainPost.deleted or mainPost.censored:
        raise serializers.ValidationError(f'帖子(id={id})不存在、已被删除或被屏蔽')

    return mainPost


def get_post_from_url(view: APIView, key_name='post_id') -> models.Post:
    """
    从url中获取一个帖子或评论对象，并确保其没有被屏蔽或删除。
    如果对象不合法，将抛出 ValidationError
    """
    postId = view.kwargs[key_name]
    return get_post_by_id(postId)

def verify_main_post(post: models.Post):
    """
    确保本帖子是主贴，否则抛出异常
    """
    if post.replyToComment or post.replyToId:
        raise serializers.ValidationError(f'只能给主贴回复，但帖子id={post.pk}不是主贴')

class EditCommentSerializer(PostSerializerMixin, serializers.Serializer):
    """
    处理一级评论的添加和修改
    """

    content = EditContentSerializer()

    @atomic
    def create(self, validated_data):

        userProfile: UserProfile = self.context['request'].user
        mainPost = get_post_from_url(self.context['view'])
        verify_main_post(mainPost)

        post = models.Post.objects.create(
            createdBy_id=userProfile.pk,
            replyToId=mainPost,
            replyToComment=None,
            # 对评论不需要检查
            viewableToGuest=True,
        )

        self.create_content(validated_data, post)

        return post

    def update(self, instance, validated_data):
        self.create_content(validated_data, instance)
        return instance

class ReadSubCommentSerializer(PostSerializerMixin, serializers.ModelSerializer):
    """
    处理二级及以上评论的读取
    """

    content = ReadContentSerializer(read_only=True)

    createdBy = serializers.CharField(label='创建者的用户名')
    creatorAvatar = serializers.URLField(label='创建者的头像', read_only=True, allow_null=True)

    replyToUser = serializers.CharField(label='回复的对象的用户名', read_only=True)

    class Meta:
        model = models.Post
        fields = ['id', 'createTime', 'replyToId',
            # 正常情况下我们不需要再声明下面两个field，但是不这么搞的话 drf_yasg 会报错
            'content', 'createdBy', 'creatorAvatar', 'replyToUser']

    def to_representation(self, instance: models.Post):
        repr = super().to_representation(instance)
        self.fill_representation(repr, instance)
        repr['replyToUser'] = resolve_username(instance.replyToId.createdBy)
        return repr

def verify_comment(post: models.Post):
    """
    确保post是一个一级评论，否则抛出异常
    """
    if not post.replyToId or post.replyToComment:
        raise ValidationError(f'comment_id 必须是一个一级回复，而id={post.pk}不是')

class EditSubCommentSerializer(PostSerializerMixin, serializers.Serializer):
    """
    处理二级及以上评论的添加和修改
    """

    content = EditContentSerializer()

    replyTo = serializers.IntegerField(label='要回复的评论的id；只在添加新评论时有效，其他情况下会'
        '忽略此值')

    @atomic
    def create(self, validated_data):

        userProfile: UserProfile = self.context['request'].user
        comment = get_post_from_url(self.context['view'], 'comment_id')
        verify_comment(comment)

        replyTarget = get_post_by_id(validated_data['replyTo'])
        if comment == replyTarget:
            pass
        elif not replyTarget.replyToId or not replyTarget.replyToComment:
            raise ValidationError('replyTo 指定的回复目标不能是主贴或一级评论，除非 replyTo = comment_id')
        elif replyTarget.replyToComment.pk != comment.pk:
            raise ValidationError('replyTo 指定的回复目标跟本评论不属于同一个一级评论。其目标'
                f'id={replyTarget.replyToComment.pk}')

        post = models.Post.objects.create(
            createdBy_id=userProfile.pk,
            replyToId=replyTarget,
            replyToComment=comment,
            # 对评论不需要检查
            viewableToGuest=True,
        )

        self.create_content(validated_data, post)

        return post

    def update(self, instance, validated_data):
        # 不能更新 replyTo
        self.create_content(validated_data, instance)
        return instance

class FavouritePostSerializer(serializers.ModelSerializer):
    post = ReadMainPostSerializer(read_only=True)
    class Meta:
        model = models.FavouritePost
        fields = ['post']
        depth = 1
        detail = False

class UserInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserInformation
        fields = ['username', 'avatarUrl']