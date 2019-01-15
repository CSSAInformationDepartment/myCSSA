
from django.urls import path, re_path, include
from myCSSAhub import views as Views
from FinanceAPI import urls as FinanceUrls
from OrganisationMgr import  urls as OrgMgrUrls

app_name = "myCSSAhub"
urlpatterns = [
    path('home/', Views.home, name="home"),
    path('under-dev/', Views.under_dev_notice, name='under-dev'),
    path('userinfo/', Views.UpdateUserProfileView.as_view(), name="userInfo"),
    path('member-card-info', Views.MembershipCardView.as_view(), name="membership-info"),
    path('message/', Views.message, name="message"),
    path('login/', Views.LoginPage.as_view(), name="hub_login"),
    path('notification/notifications_list/', Views.NotificationsList.as_view(), name="notifications_list"),
    path('notification/notifications_form/', Views.NotificationForm.as_view(),  name="notifications_form"),
    path('notification/notifications_display/<str:id>/', Views.NotificationsDisplay.as_view(), name="notifications_display"),
    path('logout/', Views.logout_page , name='hub_logout'),
    path('welcome/', Views.register_guide , name='hub_reg'),
    path('regform/', Views.NewUserSignUpView.as_view() , name='hub_regform'),
    path('regform/<str:id>/', Views.NewUserSignUpView.as_view() , name='hub_migrationreg'),
    path('userinfo/create/', Views.NewUserSignUpView.as_view(), name='hub_userinfo_create'),
    path('migration/',Views.migrationView.as_view(),name='hub_migration'),
    path('email/',Views.Email.as_view(),name='email'),
    path('reset-password/', Views.UpdatePasswordView.as_view(), name="update-password"),
]

## Admin system app directory
urlpatterns += [
    path('finance/', include(FinanceUrls, namespace='FinanceAPI')),
    path('organisation/', include(OrgMgrUrls, namespace='OrganisationMgr')),
]

## Internal AJAX path
urlpatterns += [
    path('ajax/getUserAvatar/', Views.GetUserAvatar, name="ajax_getUserAvatar"),
    path('ajax/checkEmailIntegrity/', Views.CheckEmailIntegrity, name="ajax_checkEmailIntegrity"),
    path('ajax/checkPhoneIntegrity/', Views.CheckTelIntegrity, name="ajax_checkTelIntegrity"),
    path('ajax/checkStudentIdIntegrity/', Views.CheckStudentIdIntegrity, name="ajax_checkStudentIdIntegrity"),
    path('ajax/userlookup/', Views.UserLookup.as_view(), name="ajax_userLookup"),
    path('ajax/saveBlog/', Views.saveBlog.as_view(), name="ajax_saveBlog"),
    path('ajax/deleteBlog/', Views.deleteBlog.as_view(), name="ajax_deleteBlog")
]
