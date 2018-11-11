from django.shortcuts import render
import events.models as Models
import events.serializers as ModelSerializers
from rest_framework import generics

# Create your views here.

# 活动列表API
class  EventListView(generics.ListCreateAPIView):
    queryset = Models.Event.objects.all()
    serializer_class = ModelSerializers.EventSerializers
