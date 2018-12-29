from django.contrib import admin
from django.urls import path, re_path, include
from PublicSite import views as Views

app_name = "PublicSite"
urlpatterns = [
    path('', Views.index, name='index'),
    path('news/',Views.News, name='news'),
    path('department/<str:dept>/', Views.Departments, name='departments'),
]
