from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'favouriteposts', views.FavouritePostViewSet)
router.register(r'tag', views.TagViewSet)
router.register(r'post', views.MainPostViewSet, 'post'),
# router.register(r'notification', views.UnreadNotificationViewSet, 'notification')

comment_router = routers.DefaultRouter()
comment_router.register(r'comment', views.CommentViewSet, 'comment')

subcomment_router = routers.DefaultRouter()
subcomment_router.register(r'comment', views.SubCommentViewSet, 'subcomment')

urlpatterns = [
    path('', include(router.urls)),
    path('post/<int:post_id>/', include(comment_router.urls)),
    path('comment/<int:comment_id>/', include(subcomment_router.urls)),
]
