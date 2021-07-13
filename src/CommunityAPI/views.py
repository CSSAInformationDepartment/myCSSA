from django.http import response
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create your views here.

from rest_framework import viewsets
from rest_framework import permissions
from . import serializers
from .models import Tag, Post

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    APIs to allow tags being read
    """
    queryset = Tag.objects.all().order_by('id')
    serializer_class = serializers.TagSerializer
    permission_classes = [permissions.AllowAny]

class PostListViewSet(viewsets.ReadOnlyModelViewSet):
    """
    APIs to return all posts
    """
    queryset = Post.objects.all()
    serializer_class = serializers.PostListSerializer
    permission_classes = [permissions.AllowAny]