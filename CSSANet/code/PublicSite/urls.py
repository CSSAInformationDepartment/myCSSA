from django.contrib import admin
from django.urls import path, re_path, include
from PublicSite import views as Views
from Library.SiteManagement import LoadPagetoRegister

from PhotoCompetition import public_urls as PhotoCompetitionPublicUrls
from EventAPI import public_urls as EventsPublicUrls

app_name = "PublicSite"
urlpatterns = [
    path('', Views.index, name='index'),
    path('department/<str:dept>/', Views.DepartmentInfoView.as_view(), name='departments'),
    path('contact/', Views.ContactUs, name="contact"),
    path('recruitment/', Views.Recruitments, name='recruitment'),
    path('resumes/<str:jobId>/', Views.ResumeSubmissionView.as_view(), name='resumes'),
    path('merchants/', Views.Merchants, name='merchants'),
    path('support_merchants/', Views.SupportMerchants, name='supportMerchants'),
    path('blog/<int:blogId>/', Views.BlogContents, name='blogContent'),
    path('blogs/', Views.Blogs, name='blogs'),
    path('reviewblog/', Views.reviewBlogPublic.as_view(), name='reviewBlogPublic'),
    path('events/', Views.EventsListView.as_view(), name='events'),
    path('events/<str:eventID>/', Views.EventDetails, name='eventsDetails'),

    ### Apps Extension Urls
    path('app/photo-competition/', include(PhotoCompetitionPublicUrls,  namespace='PhotoCompetition')),

    ### mobile app api
    path('app/events/', include(EventsPublicUrls,  namespace='EventAPI')),

]


## Mobile client API
from django.conf.urls import url
from rest_framework_simplejwt.views import (
    TokenObtainPairView, # 生成token
    TokenRefreshView,     # refresh token
    TokenVerifyView,   # 无需访问签名密钥即可验证HMAC签名的令牌
)
# from .serializers import MyTokenObtainPairView


urlpatterns += [
    # url(r'^api-token-auth/', views.obtain_auth_token)
    # path('jwt-auth/', views.obtain_jwt_token )
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

