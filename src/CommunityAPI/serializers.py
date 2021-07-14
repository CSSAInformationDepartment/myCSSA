from django.contrib.postgres import fields
from rest_framework import serializers
from django.db.transaction import atomic

from UserAuthAPI.models import UserProfile

from . import models

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tag
        fields = ['id', 'title']

class FavouritePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FavouritePost
        fields = ['postId']
    
    def create(self, validated_data):
        user = self.context['request'].user.id

        models.FavouritePost.create(
            user=user,
            postId=validated_data['postId']
        )
        
class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Content
        fields = ['title', 'text', 'imageUrls']
        read_only_fields = ['editedTime']

def resolve_username(profile: UserProfile) -> str:
    # 暂时用用户的全名来当作用户名
    return profile.firstNameEN + ' ' + profile.lastNameEN

class ReadPostSerializer(serializers.ModelSerializer):
    """
    只用来处理文章的读取
    """

    SUMMARY_TEXT_LENGTH = 50 # 25个汉字

    content = ContentSerializer(read_only=True)

    createdBy = serializers.CharField()

    class Meta:
        model = models.Post
        fields = ['id', 'tag_id', 'createTime', 'viewCount', 'viewableToGuest',
            # 正常情况下我们不需要再声明下面两个field，但是不这么搞的话 drf_yasg 会报错
            'content', 'createdBy']

    def to_representation(self, instance: models.Post):
        repr = super().to_representation(instance)

        contentModel = models.Content.objects.filter(post=instance).order_by('-editedTime').first()
        repr['content'] = self.fields['content'].to_representation(contentModel)

        # 如果是读取文章列表，只保留正文的前25个汉字
        if not self.context['view'].detail:
            repr['content']['text'] = repr['content']['text'][:self.SUMMARY_TEXT_LENGTH]


        repr['createdBy'] = resolve_username(instance.createdBy)

        return repr

class EditPostSerializer(serializers.ModelSerializer):
    """
    处理帖子的添加和修改。
    对于主贴而言，只有在添加的时候 tag 和 viewableToGuest 有效。其他情况下这两个字段没有用。
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

        models.Content.objects.create(
            post=post,
            editedBy_id=userProfile.pk,
            **validated_data['content']
        )

        return post

    def update(self, instance, validated_data):

        userProfile = self.context['request'].user
        # TODO: update tag and viewable to guest?

        models.Content.objects.create(
            post=instance,
            editedBy_id=userProfile.pk,
            **validated_data['content']
        )

        return instance
