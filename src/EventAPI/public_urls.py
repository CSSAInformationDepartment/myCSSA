from django.urls import path, re_path, include
from rest_framework import routers
from . import views

app_name = "EventAPI"
EventsPublic = routers.DefaultRouter()   
# PhotoCompPublic.register(r'photos',views.ApprovedSubmissionsAPIViewSet)
# EventsPublic.register(r'events-past',views.MobilePastEventAPI)
# EventsPublic.register(r'events-future',views.MobileFutureEventAPI)

urlpatterns = [
    path('mobile-api/',include(EventsPublic.urls)),
    path('mobile-api/events-past/', views.MobilePastEventAPI.as_view(), name='PastEventForMobileAPI'),
    path('mobile-api/events-future/', views.MobileFutureEventAPI.as_view(), name='FutureEventForMobileAPI'),
]
