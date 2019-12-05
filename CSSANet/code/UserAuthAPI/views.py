###############################################################################
#                    Desinged & Managed by Josh.Le.LU                         #
#                                                                             #
#                     █████╗ ██╗     ██╗ ██████╗███████╗                      #
#                    ██╔══██╗██║     ██║██╔════╝██╔════╝                      #
#                    ███████║██║     ██║██║     █████╗                        #
#                    ██╔══██║██║     ██║██║     ██╔══╝                        #
#                    ██║  ██║███████╗██║╚██████╗███████╗                      #
#                    ╚═╝  ╚═╝╚══════╝╚═╝ ╚═════╝╚══════╝                      #
#        An agile web application platform bulit on top of Python/django      #
#                                                                             #
#                Proprietary version made for myCSSA project                  #
#                             Version: 0.6a(C)                                #
#                                                                             #
###############################################################################


from rest_framework import generics,authentication,permissions, status, response
from django.contrib.auth import get_user_model, authenticate

from UserAuthAPI import models, serializers

class UserListView(generics.ListCreateAPIView):
    queryset = models.User.objects.all()
    serializer_class = serializers.LoginSerializer


class EditUserDetails(generics.GenericAPIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def post(self, request):
        self.object = self.get_object()
        serializer = serializers.UserDetailSerializer(self.object, data=request.data)
        if serializer.is_valid():
            self.object.save()
            return response(serializer.data, status=status.HTTP_200_OK)
        else:
            return response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

#class DuplicateEmailCheck(generics.GenericAPIView):
#    queryset = models.UserProfile.objects.filter('')


## for JWT test 
from rest_framework import viewsets, permissions
from .models import UserProfile
from .serializers import UserProfileSerializer
from rest_framework.exceptions import PermissionDenied

class IsOwner(permissions.BasePermission): #用于权限校验。保证用户看不到别人的信息
   
   def has_object_permission(self, request, view, obj):
       return obj.user == request.user

class UserProfileViewSet(viewsets.ModelViewSet):
   
#    queryset = UserProfile.objects.all() # 指定 queryset
   serializer_class = UserProfileSerializer # 指定序列化类
   permission_class = (IsOwner,)
   
   # 确保用户只能看到自己的数据。
   def get_queryset(self):
       
      user = self.request.user

      if user.is_authenticated:
        return UserProfile.objects.filter(user=user)

      raise PermissionDenied()
   
   # 设置当前用户为当前对象的所有者
   def perform_create(self, serializer):
       serializer.save(user = self.request.user)

