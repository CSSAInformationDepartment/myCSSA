from django.contrib import admin
from django.urls import path, re_path, include
from PublicSite import views as Views
from Library.SiteManagement import LoadPagetoRegister

app_name = "PublicSite"
urlpatterns = [
    path('', Views.index, name='index'),
    path('news/',Views.News, name='news'),
    path('department/<str:dept>/', Views.Departments, name='departments'),
    path('blog/<int:contentId>/', Views.BlogContents, name='blogContent'),
    path('blogs/<int:page>/', Views.Blogs, name='blogs')
]
