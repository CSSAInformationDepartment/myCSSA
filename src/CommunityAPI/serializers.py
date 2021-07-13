from django.contrib.postgres import fields
from rest_framework import serializers

from . import models

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tag
        fields = ['id', 'title']

class PostListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Post
        fields = ['id', 'tagId', 'contentId', 'createTime', 'createdBy', 'viewCount']

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Post
        fields = ['id', 'tagId', 'replyToId', 'replyToComment', 'viewableToGuest', 'contentId', 'createdBy']