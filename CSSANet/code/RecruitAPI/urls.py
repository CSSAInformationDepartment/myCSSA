from django.urls import path, re_path, include
from .views import *

app_name = 'RecruitAPI'

urlpatterns = [
    path('list/', JobListView.as_view(), name="job_list"),
    path('resume/', ResumeListView.as_view(), name="resume_list"),
    path('resume/<str:id>/detail/', ResumeDetailView.as_view(), name="resume_detail")
]

urlpatterns += [
    path('ajax/resumelist/', ResumeListJsonView.as_view(), name="resume_jsonlist"),
    path('ajax/joblist/', JobListJsonView.as_view(), name="job_jsonlist")
]