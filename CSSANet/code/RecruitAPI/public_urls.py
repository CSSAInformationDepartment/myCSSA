from django.urls import path, re_path, include
from rest_framework import routers
from .views import *

app_name = "RecruitAPI"
JobListAPIPublic = routers.DefaultRouter()
JobListAPIPublic.register(r'job-list', JobListAPIViewSet)

urlpatterns = [
    path('api/', include(JobListAPIPublic.urls)),
    path('jobs/<str:id>/detail/', JobDetailView.as_view(), name="job_detail")
]

