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
