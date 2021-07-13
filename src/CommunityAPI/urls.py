from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'tags', views.TagViewSet)
router.register(r'posts', views.PostListViewSet)

urlpatterns = router.urls