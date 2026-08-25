from django.urls import path

from . import views


app_name = 'MiniProgramAPI'

urlpatterns = [
    path('health', views.HealthView.as_view(), name='health'),
    path('auth/wechat-bind', views.WechatBindView.as_view(), name='wechat-bind'),

    path('upload/token', views.UploadTokenView.as_view(), name='upload-token'),
    path('uploads/complete', views.UploadCompleteView.as_view(), name='upload-complete'),

    path('users/me', views.MeView.as_view(), name='me'),
    path('users/me/posts', views.MyPostsView.as_view(), name='my-posts'),
    path('users/me/comments', views.MyCommentsView.as_view(), name='my-comments'),
    path('users/me/likes/received', views.MyLikesReceivedView.as_view(), name='likes-received'),
    path('users/me/likes/given', views.MyLikesGivenView.as_view(), name='likes-given'),
    path('users/me/reviews', views.MyReviewsView.as_view(), name='my-reviews'),

    path('messages', views.MessagesView.as_view(), name='messages'),
    path('messages/unread-count', views.UnreadCountView.as_view(), name='unread-count'),
    path('messages/read', views.MarkMessagesReadView.as_view(), name='messages-read'),

    path('posts', views.PostsView.as_view(), name='posts'),
    path('posts/<str:post_id>', views.PostDetailView.as_view(), name='post-detail'),
    path('posts/<str:post_id>/comments', views.CommentsView.as_view(), name='comments'),
    path('comments/<str:comment_id>/replies', views.RepliesView.as_view(), name='replies'),
    path('comments/<str:comment_id>', views.CommentDetailView.as_view(), name='comment-detail'),
    path('likes/toggle', views.LikeToggleView.as_view(), name='like-toggle'),

    path('courses', views.CoursesView.as_view(), name='courses'),
    path('courses/<uuid:course_id>', views.CourseDetailView.as_view(), name='course-detail'),
    path('courses/<uuid:course_id>/reviews', views.CourseReviewsView.as_view(), name='course-reviews'),
    path('reviews/<uuid:review_id>', views.ReviewDetailView.as_view(), name='review-detail'),
]
