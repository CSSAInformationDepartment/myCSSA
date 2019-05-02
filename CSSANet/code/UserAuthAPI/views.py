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


from rest_framework import generics, viewsets, filters
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAdminUser,IsAuthenticated, IsAuthenticatedOrReadOnly, BasePermission
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model, authenticate

from UserAuthAPI import models, serializers, filters


class UserListAPIView(viewsets.ReadOnlyModelViewSet):
    '''
    Retrive user profile with filtering

    Endpoint: 
        - List: /hub/api/user/user-info/
            > GET Filters: gender, joinDate_after, joinDate_before, dateOfBirth
        - Detials /hub/api/user/user-info/<id>/
    '''
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, )
    queryset = models.UserProfile.objects.all()
    serializer_class = serializers.UserDetailSerializer
    filterset_class = filters.UserProfileFilterSet

    def filter_queryset(self, queryset):
        filter_backends = (DjangoFilterBackend, )

        # Other condition for different filter backend goes here
        for backend in list(filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, view=self)
        return queryset
