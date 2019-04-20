from django.urls import path, re_path, include
from . import views

app_name = "PhotoCompetition"
urlpatterns = [
    path('submit/', views.CandidateSubmissionView.as_view(), name="submit-photo"),

]

