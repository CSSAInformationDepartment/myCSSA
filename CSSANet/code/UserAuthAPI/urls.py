
from django.urls import re_path, include
from django.contrib import admin
import rest_auth.registration.urls

from rest_framework import routers

from .views import UserListAPIView

#from rest_framework_swagger.views import get_swagger_view
app_name = "UserAuthAPI"

UserAuthRouter = routers.SimpleRouter()
UserAuthRouter.register(r'user-info', UserListAPIView)

urlpatterns = [

#  
    re_path(r'', include(UserAuthRouter.urls)),

    re_path(r'^rest-auth/', include('rest_auth.urls')),
    re_path(r'^rest-auth/registration/', include('rest_auth.registration.urls')),
    re_path(r'^account/', include('allauth.urls')),

]