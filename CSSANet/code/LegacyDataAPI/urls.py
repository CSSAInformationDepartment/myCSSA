from django.conf.urls import url
import LegacyDataAPI.views as APIViews

app_name = "LegacyDataAPI"
urlpatterns = [
    url(r'^api/checkemail', APIViews.LegacyUserLookup.as_view() , name="emailcheck"),
    url(r'^api/checkemail/get', APIViews.LegacyUserLookup.as_view() , name="emailcheck"),
]
