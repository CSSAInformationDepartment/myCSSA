from django.urls import path,re_path,include
from rest_framework import routers
from .views import *

app_name = "PhotoCompetition"

PhotoCompRouter = routers.DefaultRouter()

PhotoCompRouter.register(r'submission-list', SubmissionListAPIViewSet)

urlpatterns = [
    path('api/',include(PhotoCompRouter.urls)),
    path('api/toggle-approval/', SubmissionSelectionControlAPI.as_view(), name="toggle-approval"),
    path('inspect/<uuid:pk>/detail/', SubmissionDetailView.as_view(), name='submission-detail'),
    path('list/', SubmissionListView.as_view(), name="submission-list")
]
