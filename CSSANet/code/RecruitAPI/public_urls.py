from django.urls import path, re_path, include
from rest_framework import routers
from .views import *

app_name = "RecruitAPI"
JobListAPIPublic = routers.DefaultRouter()
JobListAPIPublic.register(r'job-list', JobListAPIViewSet)

urlpatterns = [
    # path('list/', JobListView.as_view(), name="job_list"),
    # path('resume/', ResumeListView.as_view(), name="resume_list"),
    # path('resume/<str:id>/detail/', ResumeDetailView.as_view(), name="resume_detail"),
    # path('resume/<str:id>/add_to_interview/', AddInterviewView.as_view(), name="add_to_interview"),
    path('api/', include(JobListAPIPublic.urls)),
    path('jobs/<str:id>/detail/', JobDetailView.as_view(), name="job_detail")
]

