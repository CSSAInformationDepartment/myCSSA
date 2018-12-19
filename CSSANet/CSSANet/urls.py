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
#from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path,re_path ,include

from grappelli import urls as GrappelliUrl
from filebrowser.sites import site as MediaBrowser 

from PublicSite import urls as PublicUrl
from UserAuthAPI import urls as AuthUrl
from LegacyDataAPI import urls as LegacyUrl
from myCSSAhub import urls as HubUrl


urlpatterns = [
    path('', include(PublicUrl)), 
    path('hub/',include(HubUrl)),
    path('grappelli/', include(GrappelliUrl)),
    path('admin/', admin.site.urls),
    path('admin/filebrowser/', MediaBrowser.urls),
    path('api/users/', include(AuthUrl)),
    path('api/legacy/', include(LegacyUrl))
] 

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    # Routers for Static Files and User Upload Media
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 

#print (urlpatterns)