from rest_framework import serializers

from UserAuthAPI.models import UserProfile

from . import models

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tag
        fields = ['id', 'title']

class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Content
        fields = ['title', 'text', 'imageUrls']
        read_only_fields = ['editedTime']

def resolve_username(profile: UserProfile) -> str:
    # 暂时用用户的全名来当作用户名
    return profile['lastNameCN'] + profile['firstNameCN']

class ReadPostSerializer(serializers.ModelSerializer):
    """
    只用来处理文章的读取
    """

    SUMMARY_TEXT_LENGTH = 50 # 25个汉字

    content = ContentSerializer(read_only=True)

    createdBy = serializers.CharField()

    class Meta:
        model = models.Post
        fields = ['id', 'tagId', 'createTime', 'viewCount', 
            # 正常情况下我们不需要再声明下面两个field，但是不这么搞的话 drf_yasg 会报错
            'content', 'createdBy']

    def to_representation(self, instance: models.Post):
        repr = super().to_representation(instance)

        contentModel = models.Content.objects.filter(postId=instance['id']).order_by('-editTime')
        repr['content'] = self.content.to_representation(contentModel)

        # 如果是读取文章列表，只保留正文的前25个汉字
        if not self.context['view'].detail:
            repr['content']['text'] = repr['content']['text'][:self.SUMMARY_TEXT_LENGTH]


        userProfile = UserProfile.objects.get(pk=instance['createdBy'])
        repr['createdBy'] = resolve_username(userProfile)

        return repr

class EditPostSerializer(serializers.ModelSerializer):
    content = ContentSerializer()

    class Meta:
        model = models.Post
        fields = ['tagId', 'viewableToGuest',
            # 正常情况下我们不需要再声明下面的field，但是不这么搞的话 drf_yasg 会报错
            'content']

    def create(self, validated_data):

        userId = self.context['request'].user.id

        post = models.Post.objects.create(
            createdBy=userId,
            tagId=validated_data['tagId'],
            viewableToGuest=validated_data['viewableToGuest']
        )

        models.Content.objects.create(
            postId=post.id,
            editedBy=userId,
            **validated_data['content']
        )

        return post

    def update(self, instance, validated_data):

        userId = self.context['request'].user.id

        models.Content.objects.create(
            postId=instance.id,
            editedBy=userId,
            **validated_data['content']
        )

        return instance