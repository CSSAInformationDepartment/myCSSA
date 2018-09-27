
from django.urls import path
from . import views as site

app_name = "publicSite"
urlpatterns = [
    # Url session for main site
    path('index/', site.index, name="index"),
]
