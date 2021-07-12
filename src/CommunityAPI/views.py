from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets
from rest_framework import permissions
from . import serializers
from .models import Tag

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    APIs to allow tags being read
    """
    queryset = Tag.objects.all().order_by('id')
    serializer_class = serializers.TagSerializer
    permission_classes = [permissions.AllowAny]
