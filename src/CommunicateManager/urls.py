from django.urls import path

from .views import *

app_name = "CommunicateManager"

urlpatterns = [
    path('message/', message, name="message"),
    path('notification/notifications_list/',
         NotificationsList.as_view(), name="notifications_list"),
    path('notification/notifications_form/',
         NotificationForm.as_view(),  name="notifications_form"),
    path('notification/notifications_display/<str:id>/',
         NotificationsDisplay.as_view(), name="notifications_display"),
    path('email/', Email.as_view(), name='email'),
    path('email_history/<str:id>/', EmailHistory.as_view(), name='email_history'),
    path('email_message/', Email_Message.as_view(), name="email_message"),
    path('inbox/', Inbox.as_view(), name="email_inbox"),

]
