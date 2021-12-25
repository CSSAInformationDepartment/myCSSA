from django.urls import include, path
from rest_framework import routers, viewsets

from . import api_views as views

router = routers.DefaultRouter()
router.register(r'events', views.EventViewSet, 'events')

urlpatterns = router.urls