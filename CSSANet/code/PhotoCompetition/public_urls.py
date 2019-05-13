from django.urls import path, re_path, include
from rest_framework import routers
from . import views

app_name = "PhotoCompetition"
PhotoCompPublic = routers.DefaultRouter()
PhotoCompPublic.register(r'photos',views.ApprovedSubmissionsAPIViewSet)

urlpatterns = [
    path('api/',include(PhotoCompPublic.urls)),
    path('submit/', views.CandidateSubmissionView.as_view(), name="submit-photo"),
    
]

