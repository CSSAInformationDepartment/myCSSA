from rest_framework import serializers

from . import models

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Post
        fields = ['id', 'title']
