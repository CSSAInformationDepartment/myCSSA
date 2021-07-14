from django.db.models.query import QuerySet
from django.http import response
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create your views here.

from rest_framework import viewsets
from rest_framework import permissions
from . import serializers
from .models import Tag, FavouritePost

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    APIs to allow tags being read
    """
    queryset = Tag.objects.all().order_by('id')
    serializer_class = serializers.TagSerializer
    permission_classes = [permissions.AllowAny]

class FavouritePostViewSet(viewsets.ModelViewSet):
    queryset = FavouritePost.objects.all()
    serializer_class = serializers.FavouritePostSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        queryset = self.queryset
        query_set = queryset.filter(UserId=self.request.user.id)
        return query_set