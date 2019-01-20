
from django.urls import path, re_path, include
from BlogAPI import views as Views

app_name = "Blog"
urlpatterns = [
    path('editbg', Views.editBlog.as_view(), name='editblog'),
]

## Internal AJAX path
urlpatterns += [
    path('ajax/saveBlog/', Views.saveBlog.as_view(), name="ajax_saveBlog"),
    path('ajax/deleteBlog/', Views.deleteBlog.as_view(), name="ajax_deleteBlog")
]
