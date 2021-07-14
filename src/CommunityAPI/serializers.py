from django.contrib.postgres import fields
from rest_framework import serializers

from . import models

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tag
        fields = ['id', 'title']

class FavouritePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FavouritePost
        fields = ['userId', 'postId']