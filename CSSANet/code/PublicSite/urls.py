from django.contrib import admin
from django.urls import path, re_path, include
from PublicSite import views as Views
from Library.SiteManagement import LoadPagetoRegister

app_name = "PublicSite"
urlpatterns = [
    path('', Views.index, name='index'),
    path('department/<str:dept>/', Views.Departments, name='departments'),
    path('contact/', Views.ContactUs, name="contact"),
    path('recruitment/', Views.Recruitments, name='recruitment'),
    path('resumes/<str:jobId>/', Views.ResumeSubmissionView.as_view(), name='resumes'),
    path('merchants/', Views.Merchants, name='merchants'),
    path('blog/<int:blogId>/', Views.BlogContents, name='blogContent'),
    path('blogs/', Views.Blogs, name='blogs'),
    path('reviewblog/', Views.reviewBlogPublic.as_view(), name='reviewBlogPublic')
]
