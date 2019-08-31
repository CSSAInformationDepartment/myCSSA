from django.urls import path, re_path, include
from rest_framework import routers
from . import views

app_name = "RecruitAPI"
JobListAPIPublic = routers.DefaultRouter()
JobListAPIPublic.register(r'job-list',views.JobListAPIViewSet)

urlpatterns = [
    # path('api/',include(PhotoCompPublic.urls)),
    # path('api/vote/',views.VoteSubmissionControlAPI.as_view(),name='vote-photo'),
    # path('submit/', views.CandidateSubmissionView.as_view(), name="submit-photo"),
    # path('vote/',views.AxiosTestView.as_view(), name='vote'),
    path('api/', include(JobListAPIPublic.urls)),
    
]

