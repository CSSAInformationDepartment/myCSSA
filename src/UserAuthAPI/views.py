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
from django.contrib.auth import get_user_model, authenticate

from rest_framework import authentication, permissions, status, response
from rest_framework.parsers import JSONParser
from rest_framework.response import Response, Serializer
from rest_framework.decorators import api_view,permission_classes,authentication_classes
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, ListCreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from mail_owl.utils import AutoMailSender

from UserAuthAPI import models, forms, serializers

class UserListView(ListCreateAPIView):
    queryset = models.User.objects.all()
    serializer_class = serializers.LoginSerializer


class EditUserDetails(GenericAPIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def post(self, request):
        self.object = self.get_object()
        serializer = serializers.UserDetailSerializer(self.object, data=request.data)
        if serializer.is_valid():
            self.object.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([])
def user_easy_registry_api(request):
    data = JSONParser().parse(request)
    serializer = serializers.UserEasyRegistrationSerializer(data=data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        res = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
        return Response(res, status=status.HTTP_201_CREATED)

    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_login_user_info(request):
    loginUser = request.user
    userProfile = models.UserProfile.objects.filter(user=loginUser)[0]

    return Response({
        'firstname': userProfile.firstNameEN,
        'lastname': userProfile.lastNameEN,
        'telNumber': loginUser.telNumber,
        'email_addr': loginUser.email,
        'studentId': userProfile.studentId,
        'membershipId': userProfile.membershipId,
        'avatarUrl': userProfile.avatar.url
    })