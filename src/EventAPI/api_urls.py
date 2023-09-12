from rest_framework import routers

from . import api_views as views

router = routers.DefaultRouter()
router.register(r'events', views.EventViewSet, 'events')

urlpatterns = router.urls
