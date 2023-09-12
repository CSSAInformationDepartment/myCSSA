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
import base64

from django.core.files.base import ContentFile
from rest_framework import authentication, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import GenericAPIView, ListCreateAPIView
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from UserAuthAPI import models, serializers


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
        serializer = serializers.UserDetailSerializer(
            self.object, data=request.data)
        if serializer.is_valid():
            self.object.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        'avatarUrl': userProfile.avatar.url if userProfile.avatar else 'None'
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_user_avatar(request):
    model = models.UserProfile
    current_user = model.objects.get(user=request.user)
    data = JSONParser().parse(request)
    if data["img_base64"]:
        img_b64 = data["img_base64"]
        # print(data["img_base64"])

        format, imgstr = img_b64.split(';base64,')
        ext = format.split('/')[-1]

        # Patch to avoid incorrect padding caused by some browsers
        missing_padding = len(imgstr) % 4
        if missing_padding:
            imgstr += b'=' * (4 - missing_padding)

        decoded_file = ContentFile(
            base64.b64decode(imgstr), name='avatar_lg.' + ext)
        current_user.avatar = decoded_file
        current_user.save()
        return Response(status=status.HTTP_200_OK)

    return Response(status=status.HTTP_400_BAD_REQUEST)
