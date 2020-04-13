from rest_framework import routers
from .views import MailDraftViewSet, MailQueneViewSet
from django.urls import path,include

app_name = 'mail_owl'

postman_router = routers.SimpleRouter()
postman_router.register(r'draft', MailDraftViewSet)
postman_router.register(r'quene', MailQueneViewSet)

urlpatterns = [
    path('api/', include(postman_router.urls))
]
