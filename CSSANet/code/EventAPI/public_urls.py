from django.urls import path, re_path, include
from rest_framework import routers
from . import views

app_name = "EventAPI"
EventsPublic = routers.DefaultRouter()   

# For mobile-app api
# router = routers.SimpleRouter()
# router.register('mobile-api', MobileAppViewSet, base_name="mobile_event") 注册路由
# urlpatterns = router.urls


urlpatterns = [
    path('mobile-api/',include(EventsPublic.urls)),
    path('mobile-api/events-past/', views.MobilePastEventAPI.as_view(), name='PastEventForMobileAPI'),
    path('mobile-api/events-future/', views.MobileFutureEventAPI.as_view(), name='FutureEventForMobileAPI'),
]
