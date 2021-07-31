from django.urls.conf import path, re_path

from . import hub_views as views

app_name = 'CommunityAPI'
urlpatterns = [
    re_path(r'show_post', views.ShowPostView.as_view(), name='show_post'),
]