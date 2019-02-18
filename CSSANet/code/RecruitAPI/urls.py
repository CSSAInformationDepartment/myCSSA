from django.urls import path, re_path, include
from .views import *

app_name = 'RecruitAPI'

urlpatterns = [
    path('list/', JobListView.as_view(), name="job_list")
]

urlpatterns += [
    path('ajax/list/', JobListJsonView.as_view(), name="job_jsonlist")
]