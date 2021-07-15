from django.http.response import JsonResponse
from django.shortcuts import render

# Create your views here.

from typing import TypeVar, Callable

from rest_framework import status, viewsets, permissions, mixins
from rest_framework.decorators import action, permission_classes
from drf_yasg.utils import swagger_auto_schema
from rest_framework.fields import empty
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from CommunityAPI.paginations import PostResultsSetPagination

from CommunityAPI.permissions import IsOwner
from .serializers import TagSerializer, EditPostSerializer, ReadPostSerializer, NotificationSerializer
from .models import Notification, Post, Tag

# 相关的后端开发文档参见： https://dev.cssaunimelb.com/doc/rest-framework-sSVw9rou1R

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
        其中，有分页的 GET 只返回截取正文的前 50 个字符
        通过ID读取到的文章则包含全文。
    DELETE: 删除帖子
    """

    serializer_class = ReadPostSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = (JWTAuthentication,)
    pagination_class = PostResultsSetPagination
    
    def get_queryset(self):
        query = Post.objects.filter(
            censored=False, 
            deleted=False, 
            replyToId=None, 
            replyToComment=None,
            )

        if self.request.user.is_anonymous:
            query = query.filter(viewableToGuest=True)

        # 如果想要这个功能的话，可以在这里让管理员能看见被屏蔽和删除的文章

        return query.order_by('-createTime')

    def get_permissions(self):
        if self.action == 'destroy':
            # 对于自动生成的方法（比如这里的destroy），需要在这里指定权限
            # 权限必须是一个实例，而上面的 permission_classes 必须是类名
            return [IsOwner()] 
        else:
            return super().get_permissions()

    # 在swagger文档里的条目定义：
    @swagger_auto_schema(method='POST', operation_description='添加一个帖子',
        request_body=EditPostSerializer, responses={201: ReadPostSerializer})
    # 给 rest_framework 用的view定义（这两个decorator的顺序不能反）
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
        # 通过后缀名 _id 可以直接传 id。不加后缀的时候需要传进去一个 model instance
        # 不知道为啥， request.user 不能直接传，只能用它的id
        instance.deletedBy_id = self.request.user.id
        instance.save()

    @swagger_auto_schema(method='POST', operation_description='修改帖子，不能修改 tag 和 viewableToGuest',
        request_body=EditPostSerializer, responses={202: ReadPostSerializer})
    @action(methods=['POST'], detail=True, url_path='edit', url_name='edit_post',
        serializer_class=EditPostSerializer, permission_classes=[IsOwner])
    def edit_post(self, request, pk=None):
        instance = self.get_object()
        serializer = self._create_serializer(EditPostSerializer, 
            instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        post = serializer.save()

        # 从 super().update 里复制来的代码（估计是缓存用的）
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

class UnreadNotificationViewSet(viewsets.ReadOnlyModelViewSet):
     # 在swagger文档里的条目定义：
    @swagger_auto_schema(method='Get', operation_description='显示未读消息',
        request_body= NotificationSerializer)
    def showUnreadNotification(request):
        if request.method == 'Get':
            UnreadNotification = Notification.objects.filter(read = False)
            serializer = NotificationSerializer(UnreadNotification, many = True)
            return JsonResponse(serializer.data, safe = False)

