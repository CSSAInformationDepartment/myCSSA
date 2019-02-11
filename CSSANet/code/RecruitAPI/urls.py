from django.urls import path, re_path, include
from .views import JobListJsonView

app_name = 'RecruitAPI'

urlpatterns = [
    path('list/', JobListJsonView.as_view(), name="job_list")
]