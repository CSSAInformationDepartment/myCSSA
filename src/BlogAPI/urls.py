from django.urls import path

from BlogAPI import views as Views

app_name = "Blog"
urlpatterns = [
    path('editbg', Views.editBlog.as_view(), name='editblog'),
    path('writtenBlogs', Views.writtenBlogs.as_view(), name='writtenBlogs'),
    path('reviewBlogs', Views.reviewBlogs.as_view(), name='reviewBlogs')
]

# Internal AJAX path
urlpatterns += [
    path('ajax/saveBlog/', Views.saveBlog.as_view(), name="ajax_saveBlog"),
    path('ajax/deleteBlog/', Views.deleteBlog.as_view(), name="ajax_deleteBlog"),
    path('ajax/reviewBlog/', Views.reviewBlogAjax.as_view(), name="ajax_deleteBlog")
]
