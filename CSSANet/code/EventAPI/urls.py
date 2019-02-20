from django.urls import path, re_path, include
from .views import *

app_name = "EventAPI"
urlpatterns = [
    path('list/', EventListView.as_view(), name='event_list'),
    path('list/?attended=True', EventListView.as_view(), name='events_attended'),
    path('add_event/', AddEventView.as_view(), name='add_event'),
]

urlpatterns +=[
    path('api/list/', EventListJsonView.as_view(), name="events_json")
]