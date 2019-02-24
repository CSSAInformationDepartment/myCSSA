from django.urls import path, re_path, include
from .views import *

app_name = "EventAPI"
urlpatterns = [
    path('list/', EventListView.as_view(), name='event_list'),
    path('list/?attended=True', EventListView.as_view(), name='events_attended'),
    path('add_event/', AddEventView.as_view(), name='add_event'),
    path('change/<str:id>/',UpdateEventView.as_view(), name='update_event'),
    path('confirm_order/<str:id>/',ConfirmEventOrderView.as_view(), name='confirm_order'),
    path('confirm_order/<str:id>/enroll/', EnrollEventPOSTView.as_view(), name='enroll_event')
]

urlpatterns +=[
    path('api/list/', EventListJsonView.as_view(), name="events_json")
]