from django.urls import include, path
from rest_framework import routers

from . import views

app_name = "PhotoCompetition"
PhotoCompPublic = routers.DefaultRouter()
PhotoCompPublic.register(r'photos', views.ApprovedSubmissionsAPIViewSet)

urlpatterns = [
    path('api/', include(PhotoCompPublic.urls)),
    path('api/vote/', views.VoteSubmissionControlAPI.as_view(), name='vote-photo'),
    path('submit/', views.CandidateSubmissionView.as_view(), name="submit-photo"),
    path('vote/', views.AxiosTestView.as_view(), name='vote'),
    path('result-display/', views.resultDisplay.as_view(), name='result-display')
]
