from django.contrib import admin
from django.urls import path, re_path, include
from PublicSite import views as Views

urlpatterns = [
    path('', Views.index, name='PublicSite'),
    path('news/',Views.News, name='News'),
    re_path(r'^department/(?P<dept>[\w-]+)/$', Views.Departments, name='departments-page')
]
