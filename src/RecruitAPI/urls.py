from django.urls import path

from .views import *

app_name = 'RecruitAPI'

urlpatterns = [
    path('list/', JobListView.as_view(), name="job_list"),
    path('resume/', ResumeListView.as_view(), name="resume_list"),
    path('resume/<str:id>/detail/',
         ResumeDetailView.as_view(), name="resume_detail"),
    path('resume/<str:id>/add_to_interview/',
         AddInterviewView.as_view(), name="add_to_interview"),
    path('joblist_availability_check/', JoblistAvailabilityViewSet.as_view(
        {'get': 'list'}), name='joblist_availability_check')
]

urlpatterns += [
    path('ajax/resumelist/', ResumeListJsonView.as_view(), name="resume_jsonlist"),
    path('ajax/joblist/', JobListJsonView.as_view(), name="job_jsonlist"),
    path('ajax/interview_time/', InterviewListJsonView.as_view(),
         name='interview_jsonlist'),
]
