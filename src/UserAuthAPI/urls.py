
from django.conf.urls import include
from django.urls import path, re_path
from django.views.generic import RedirectView, TemplateView

from . import views

# from rest_framework_swagger.views import get_swagger_view
app_name = "UserAuthAPI"
urlpatterns = [
    #    url(r'^$', TemplateView.as_view(template_name="home.html"), name='home'),
    #    url(r'^signup/$', TemplateView.as_view(template_name="signup.html"),
    #        name='signup'),
    re_path(r'^email-verification/$',
            TemplateView.as_view(template_name="email_verification.html"),
            name='email-verification'),
    re_path(r'^login/$', TemplateView.as_view(template_name="login.html"),
            name='login'),
    re_path(r'^logout/$', TemplateView.as_view(template_name="logout.html"),
            name='logout'),
    re_path(r'^password-reset/$',
            TemplateView.as_view(template_name="password_reset.html"),
            name='password-reset'),
    re_path(r'^password-reset/confirm/$',
            TemplateView.as_view(template_name="password_reset_confirm.html"),
            name='password-reset-confirm'),
    re_path(r'^user-details/$',
            TemplateView.as_view(template_name="user_details.html"),
            name='user-details'),
    re_path(r'^password-change/$',
            TemplateView.as_view(template_name="password_change.html"),
            name='password-change'),


    # this url is used to generate email content
    #    url(r'^password-reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    #        TemplateView.as_view(template_name="password_reset_confirm.html"),
    #        name='password_reset_confirm'),

    re_path(r'^rest-auth/', include('rest_auth.urls')),
    re_path(r'^rest-auth/registration/',
            include('rest_auth.registration.urls')),
    re_path(r'^account/', include('allauth.urls')),
    re_path(r'^accounts/profile/$', RedirectView.as_view(url='/',
            permanent=True), name='profile-redirect'),
    path('login-user-info/', views.get_login_user_info, name='login-info'),
    path('register/', views.user_easy_registry_api, name='register-api'),
    path('update-user-avatar/', views.update_user_avatar, name='update-avatar')
]
