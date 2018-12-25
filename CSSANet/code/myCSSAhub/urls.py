
from django.urls import path, re_path
from myCSSAhub import views as Views

app_name = "myCSSAhub"
urlpatterns = [
    path('home/', Views.home, name="home"),
    path('userinfo/', Views.userInfo, name="userInfo"),
    path('message/', Views.message, name="message"),
    path('notifications/', Views.notifications, name="notifications"),
    path('login/', Views.LoginPage.as_view(), name="hub_login"),
    path('logout/', Views.logout_page , name='hub_logout'),
    path('register/', Views.register_guide , name='hub_reg'),
    path('regform/', Views.BasicSignInView.as_view() , name='hub_regform'),
    path('userinfo/create/', Views.UserProfileCreateView.as_view(), name='hub_userinfo_create'),
]

## Internal AJAX path
urlpatterns += [
    path('ajax/getUserAvatar/', Views.GetUserAvatar, name="ajax_getUserAvatar"),
    path('ajax/checkEmailIntegrity/', Views.CheckEmailIntegrity, name="ajax_checkEmailIntegrity"),
    path('ajax/checkPhoneIntegrity/', Views.CheckTelIntegrity, name="ajax_checkTelIntegrity"),
]