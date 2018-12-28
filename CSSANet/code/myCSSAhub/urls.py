
from django.urls import path, re_path, include
from myCSSAhub import views as Views
from FinanceAPI import urls as FinanceUrls

app_name = "myCSSAhub"
urlpatterns = [
    path('home/', Views.home, name="home"),
    path('userinfo/', Views.userInfo, name="userInfo"),
    path('message/', Views.message, name="message"),
    path('login/', Views.LoginPage.as_view(), name="hub_login"),
    path('notification/notifications_list/', Views.notifications_list, name="notifications_list"),
    path('notification/notifications_form/', Views.notifications_form, name="notifications_form"),
    path('notification/notifications_display/', Views.notifications_display, name="notifications_display"),
    path('logout/', Views.logout_page , name='hub_logout'),
    path('register/', Views.register_guide , name='hub_reg'),
    path('regform/', Views.BasicSignInView.as_view() , name='hub_regform'),
    path('userinfo/create/', Views.UserProfileCreateView.as_view(), name='hub_userinfo_create'),
]

## Admin system app directory
urlpatterns += [
    path('finance/', include(FinanceUrls, namespace='FinanceAPI')),
]

## Internal AJAX path
urlpatterns += [
    path('ajax/getUserAvatar/', Views.GetUserAvatar, name="ajax_getUserAvatar"),
    path('ajax/checkEmailIntegrity/', Views.CheckEmailIntegrity, name="ajax_checkEmailIntegrity"),
    path('ajax/checkPhoneIntegrity/', Views.CheckTelIntegrity, name="ajax_checkTelIntegrity"),
    path('ajax/checkStudentIdIntegrity/', Views.CheckStudentIdIntegrity, name="ajax_checkStudentIdIntegrity")
]