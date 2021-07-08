"""CSSANet URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django import views
from django.conf import settings
from django.contrib import admin
from django.urls import path,re_path ,include
from django.conf.urls import handler400, handler403, handler404, handler500
from django.views.defaults import server_error

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
import CommunityAPI

from PublicSite import urls as PublicUrl
from UserAuthAPI import urls as AuthUrl
from LegacyDataAPI import urls as LegacyUrl
from myCSSAhub import urls as HubUrl
from MobileAppAPI import urls as MobileUrl
from CommunityAPI import urls as CommunityUrl

urlpatterns = [
    path('', include(PublicUrl)), 
    path('hub/',include(HubUrl)),
    path('admin/', admin.site.urls),
    path('api/users/', include(AuthUrl)),
    path('api/legacy/', include(LegacyUrl)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('oauth/', include('social_django.urls', namespace='social')),
    path('mobile/', include(MobileUrl)),
    path('api/community/', include(CommunityUrl)),
] 
handler400 = 'PublicSite.views.bad_request'
handler403 = 'PublicSite.views.permission_denied'
handler404 = 'PublicSite.views.page_not_found'
handler500 = 'PublicSite.views.server_error'

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    # Routers for Static Files and User Upload Media
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)