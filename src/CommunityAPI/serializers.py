from django.contrib.postgres import fields
from django.core.exceptions import ValidationError
from rest_framework import serializers
from django.db.transaction import atomic
from rest_framework.views import APIView

from UserAuthAPI.models import UserProfile

from . import models

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tag
        fields = ['id', 'title']

class NotificationSerializer(serializers.ModelSerializer):
   
        model = models.Notification
        fields = ['targetPost','data', 'type', 'read']

class FavouritePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FavouritePost
        fields = ['post']

    @atomic
    def create(self, validated_data):
        userProfile: UserProfile = self.context['request'].user

        favourite = models.FavouritePost.objects.create(
            user_id=userProfile.pk,
            post=validated_data['post']
        )

        return favourite
        
class ContentSerializer(serializers.ModelSerializer):

    TEXT_LENGTH_MIN=1
    TITLE_LENGTH_MIN=1

    class Meta:
        model = models.Content
        fields = ['title', 'text', 'editedTime']
        # fields = ['title', 'text', 'imageUrls', 'editedTime']
        read_only_fields = ['editedTime']

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

        ret = super().validate(attrs)

        # 如果没有这一个field，代表没有图片
        if not ret.get('imageUrls'):
            ret['imageUrls'] = []

        return ret

def resolve_username(profile: UserProfile) -> str:
    # 暂时用用户的全名来当作用户名
    return profile.firstNameEN + ' ' + profile.lastNameEN

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

        contentModel = models.Content.objects.filter(post=instance).order_by('-editedTime').first()
        repr['content'] = self.fields['content'].to_representation(contentModel)

        repr['createdBy'] = resolve_username(instance.createdBy)

    def create_content(self, validated_data, post: models.Post):
        """
        从输入的json创建一个新的content版本
        """

        userProfile: UserProfile = self.context['request'].user

        # TODO: 上传图片之类的代码写在这里

        return models.Content.objects.create(
            post=post,
            editedBy_id=userProfile.pk,
            **validated_data['content']
        )

class ReadMainPostSerializer(PostSerializerMixin, serializers.ModelSerializer):
    """
    只用来处理主贴的读取
    """

    SUMMARY_TEXT_LENGTH = 50 # 25个汉字

    content = ContentSerializer(read_only=True)

    createdBy = serializers.CharField(label='创建者的用户名')

    class Meta:
        model = models.Post
        fields = ['id', 'tag', 'createTime', 'viewCount', 'viewableToGuest',
            # 正常情况下我们不需要再声明下面两个field，但是不这么搞的话 drf_yasg 会报错
            'content', 'createdBy']

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
    content = ContentSerializer()

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

    content = ContentSerializer(read_only=True)

    createdBy = serializers.CharField(label='创建者的用户名')

    class Meta:
        model = models.Post
        fields = ['id', 'createTime',
            # 正常情况下我们不需要再声明下面两个field，但是不这么搞的话 drf_yasg 会报错
            'content', 'createdBy']

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

class EditCommentSerializer(PostSerializerMixin, serializers.Serializer):
    """
    处理一级评论的添加和修改
    """

    content = ContentSerializer()

    @atomic
    def create(self, validated_data):

        userProfile: UserProfile = self.context['request'].user
        mainPost = get_post_from_url(self.context['view'])

        if mainPost.replyToComment or mainPost.replyToId:
            raise serializers.ValidationError(f'只能给主贴回复，但帖子id={mainPost.pk}不是主贴')

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

    content = ContentSerializer(read_only=True)

    createdBy = serializers.CharField(label='创建者的用户名')

    replyToUser = serializers.CharField(label='回复的对象的用户名')

    class Meta:
        model = models.Post
        fields = ['id', 'createTime',
            # 正常情况下我们不需要再声明下面两个field，但是不这么搞的话 drf_yasg 会报错
            'content', 'createdBy', 'replyToUser']

    def to_representation(self, instance: models.Post):
        repr = super().to_representation(instance)
        self.fill_representation(repr, instance)
        repr['replyToUser'] = resolve_username(instance.replyToId)
        return repr

class EditSubCommentSerializer(PostSerializerMixin, serializers.Serializer):
    """
    处理二级及以上评论的添加和修改
    """

    content = ContentSerializer()

    replyTo = serializers.IntegerField(label='要回复的评论的id；只在添加新评论时有效，其他情况下会'
        '忽略此值')

    @atomic
    def create(self, validated_data):

        userProfile: UserProfile = self.context['request'].user
        comment = get_post_from_url(self.context['view'], 'comment_id')

        if not comment.replyToId or comment.replyToComment:
            raise ValidationError(f'comment_id 必须是一个一级回复，而id={comment.pk}不是')

        replyTarget = get_post_by_id(validated_data['replyTo'])
        if replyTarget.replyToComment.pk != comment.pk:
            raise ValidationError(f'replyTo 指定的回复目标跟本评论不属于同一个一级评论。其目标'
                'id={replyTarget.replyToComment.pk}')

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
