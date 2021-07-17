from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'favouriteposts', views.FavouritePostViewSet)
router.register(r'tag', views.TagViewSet)
router.register(r'post', views.PostViewSet, 'post')

urlpatterns = router.urls
