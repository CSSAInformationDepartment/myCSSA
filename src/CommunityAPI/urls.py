from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'tag', views.TagViewSet)
router.register(r'post', views.PostViewSet, 'post')
router.register(r'notification', views.UnreadNotificationViewSet, 'get')

urlpatterns = router.urls
