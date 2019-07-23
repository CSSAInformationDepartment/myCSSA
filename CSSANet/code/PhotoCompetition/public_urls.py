from django.urls import path, re_path, include
from rest_framework import routers
from . import views

app_name = "PhotoCompetition"
PhotoCompPublic = routers.DefaultRouter()
PhotoCompPublic.register(r'photos',views.ApprovedSubmissionsAPIViewSet)

urlpatterns = [
    path('api/',include(PhotoCompPublic.urls)),
    path('api/vote/',views.VoteSubmissionControlAPI.as_view(),name='vote-photo'),
    path('submit/', views.CandidateSubmissionView.as_view(), name="submit-photo"),
    path('vote/',views.AxiosTestView.as_view(), name='vote'),
    
]

