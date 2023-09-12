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
from django.conf import settings
from django.contrib import admin
from django.urls import path, re_path, include
from django.conf.urls import handler400, handler403, handler404, handler500

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from PublicSite import urls as PublicUrl
from UserAuthAPI import urls as AuthUrl
from LegacyDataAPI import urls as LegacyUrl
from myCSSAhub import urls as HubUrl
from MobileAppAPI import urls as MobileUrl
from CommunityAPI import urls as CommunityUrl
from EventAPI import api_urls as EventApiUrl

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

import debug_toolbar

schema_view = get_schema_view(
    openapi.Info(
        title="CSSANet API",
        default_version='v1',
        description="The document of the api of cssanet",
    ),
    public=True,
    authentication_classes=[],
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('', include(PublicUrl)),
    path('hub/', include(HubUrl)),
    path('admin/', admin.site.urls),
    path('api/users/', include(AuthUrl)),
    path('api/legacy/', include(LegacyUrl)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('oauth/', include('social_django.urls', namespace='social')),
    path('mobile/', include(MobileUrl)),
    path('api/community/', include(CommunityUrl)),
    path('api/event/', include(EventApiUrl)),

    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger',
            cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc',
            cache_timeout=0), name='schema-redoc'),

    # Routers for Debug Toolbar
    path('__debug__/', include(debug_toolbar.urls))
]
handler400 = 'PublicSite.views.bad_request'
handler403 = 'PublicSite.views.permission_denied'
handler404 = 'PublicSite.views.page_not_found'
handler500 = 'PublicSite.views.server_error'

if settings.DEBUG:
    from django.conf.urls.static import static
    # Routers for Static Files and User Upload Media
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
