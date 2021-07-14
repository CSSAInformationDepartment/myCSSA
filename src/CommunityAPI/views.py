from django.shortcuts import render

# Create your views here.

from typing import TypeVar, Callable

from rest_framework import status, viewsets, permissions, mixins
from rest_framework.decorators import action, permission_classes
from drf_yasg.utils import swagger_auto_schema
from rest_framework.fields import empty
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from CommunityAPI.permissions import IsOwner
from .serializers import TagSerializer, EditPostSerializer, ReadPostSerializer
from .models import Post, Tag

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    APIs to allow tags being read
    """
    queryset = Tag.objects.all().order_by('id')
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]

class PostViewSet(viewsets.ReadOnlyModelViewSet, mixins.DestroyModelMixin):
    """
    GET: 获取帖子
    POST: 添加帖子
    DELETE: 删除帖子
    """

    serializer_class = ReadPostSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = (JWTAuthentication,)
    
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

    @swagger_auto_schema(method='POST', operation_description='添加一个帖子',
        request_body=EditPostSerializer, responses={201: ReadPostSerializer})
    @action(methods=['POST'], detail=False, url_path='create', url_name='create_post',
        serializer_class=EditPostSerializer,
        permission_classes=[permissions.IsAuthenticated])
    def create_post(self, request):
        serializer = self._create_serializer(EditPostSerializer, data=request.data)
        serializer.is_valid(raise_exception=True)
        post = serializer.save()
        result = self._create_serializer(ReadPostSerializer, instance=post).data
        return Response(data=result, status=status.HTTP_201_CREATED)


    def perform_destroy(self, instance: Post):
        instance.deleted = True
        instance.deletedBy = self.request.user.id
        instance.save()

    @swagger_auto_schema(method='POST', operation_description='修改帖子',
        request_body=EditPostSerializer, responses={202: ReadPostSerializer})
    @action(methods=['POST'], detail=True, url_path='edit', url_name='edit_post',
        serializer_class=EditPostSerializer, permission_classes=[IsOwner])
    def edit_post(self, request, pk=None):
        instance = self.get_object()
        serializer = self._create_serializer(EditPostSerializer, 
            instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        post = serializer.save()

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        result = self._create_serializer(ReadPostSerializer, instance=post).data
        return Response(data=result, status=status.HTTP_202_ACCEPTED)

    T = TypeVar('T')
    def _create_serializer(self, serializer: Callable[..., T], instance=None, data=empty) -> T:
        """
        使用context创建一个 serializer
        """
        return serializer(instance=instance, data=data, 
            context=self.get_serializer_context())
