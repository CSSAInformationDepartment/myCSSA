
from django.urls import path
from events import views as events

app_name = "event"
urlpatterns = [
    path('api/list/', events.EventListView.as_view() , name="home"),
]
