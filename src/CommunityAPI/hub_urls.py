from django.urls.conf import path, re_path

from . import hub_views as views

app_name = 'CommunityAPI'
urlpatterns = [
    re_path(r'show_post', views.ShowPostView.as_view(), name='show_post'),
    path('post_list', views.PostListView.as_view(), name='post_list'),
    path('post_list_json', views.PostListJsonView.as_view(), name='post_list_json'),
]
