from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets
from rest_framework import permissions
from . import serializers
from .models import Post, Tag

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    APIs to allow tags being read
    """
    queryset = Tag.objects.all().order_by('id')
    serializer_class = serializers.TagSerializer
    permission_classes = [permissions.AllowAny]

class PostReadViewSet(viewsets.ReadOnlyModelViewSet):
    """
    读取帖子
    """

    serializer_class = serializers.PostReadSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        query = Post.objects.filter(
            censored=False, 
            deleted=False, 
            replyToId=None, 
            replyToComment=None,
            )

        if not self.request.user:
            query = query.filter(viewableToGuest=True)

        # 如果想要这个功能的话，可以在这里让管理员能看见被屏蔽和删除的文章

        return query.order_by('-createTime')