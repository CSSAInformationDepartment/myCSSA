
from django.urls import path, re_path, include
from django.contrib.auth import views as auth_views

from myCSSAhub import views as Views
from FinanceAPI import urls as FinanceUrls
from OrganisationMgr import  urls as OrgMgrUrls
from BlogAPI import urls as BlogUrls
from RecruitAPI import urls as RecruitUrls
from EventAPI import urls as EventUrls
from FlexForm import urls as FlexFormUrls
from CommunicateManager import urls as CommUrls
from PhotoCompetition import hub_urls as PhotoCompUrls
from CommunityAPI import hub_urls as CommunityUrls

from PrizeAPI.views import (LuckyDrawDataView,LuckyDrawEventView,LuckyDrawView)

app_name = "myCSSAhub"
urlpatterns = [
    path('home/', Views.home, name="home"),
    path('under-dev/', Views.under_dev_notice, name='under-dev'),
    path('userinfo/', Views.UpdateUserProfileView.as_view(), name="userInfo"),
    path('userinfo/update-avatar/', Views.UpdateUserAvatarView.as_view(), name="update_user_avatar"),
    path('member-card-info', Views.MembershipCardView.as_view(), name="membership-info"),
    path('login/', Views.LoginPage.as_view(), name="hub_login"), 
    path('logout/', Views.logout_page , name='hub_logout'),
    path('welcome/', Views.register_guide , name='hub_reg'),
    # path('regform/', Views.NewUserSignUpView.as_view() , name='hub_regform'),
    # path('regform/<str:id>/', Views.NewUserSignUpView.as_view() , name='hub_migrationreg'),
    # path('userinfo/create/', Views.NewUserSignUpView.as_view(), name='hub_userinfo_create'),
    path('regform/', Views.EasyRegistrationView.as_view() , name='hub_regform'),
    path('regform/<str:id>/', Views.EasyRegistrationView.as_view() , name='hub_migrationreg'),
    path('userinfo/create/', Views.EasyRegistrationView.as_view(), name='hub_userinfo_create'),
    path('reg/success/', Views.EasyConfirmationPage, name='hub_regformConfirmation'),
    path('migration/',Views.migrationView.as_view(), name='hub_migration'),
    path('reset-password/', Views.UpdatePasswordView.as_view(), name="update-password"),
    path('merchants_list/', Views.Merchants_list.as_view(), name="merchants_list"),
    path('merchant_add/', Views.Merchant_add.as_view(), name="merchants_add"),
    path('merchant_profile/<str:id>/', Views.Merchant_profile.as_view(), name="merchant_profile"),
    path('calendar/', Views.Calendar.as_view(), name="calendar"),
    # path('luckydraw/', LuckyDrawView.as_view(), name="luckydraw"),
    path('luckydraw/event_pool/',LuckyDrawEventView.as_view(), name="luckydraw_event_list"),
    path('luckydraw/event_pool/<str:id>/',LuckyDrawView.as_view(), name="luckydraw_event_draw"),
    path('password_reset/', Views.PasswordResetView.as_view(), name="password_reset"),
    path('password_reset/<uidb64>/<token>/', Views.PasswordResetConfirmView.as_view(template_name="password_reset_confirm.html"), name='password_reset_confirm'),
]
    

## System app directory
urlpatterns += [
    path('finance/', include(FinanceUrls, namespace='FinanceAPI')),
    path('organisation/', include(OrgMgrUrls, namespace='OrganisationMgr')),
    path('blog/', include(BlogUrls, namespace="BlogAPI")),
    path('recruit/', include(RecruitUrls, namespace="RecruitAPI")),
    path('event/', include(EventUrls, namespace="EventAPI")),
    path('flexform/', include(FlexFormUrls, namespace="FlexForm")),
    path('communication/',include(CommUrls, namespace='Comm')),
    path('photo-competition/', include(PhotoCompUrls, namespace='PhotoComp')),
    path('community/', include(CommunityUrls, namespace='CommunityAPI')),
]

## Internal AJAX path
urlpatterns += [
    path('ajax/getUserAvatar/', Views.GetUserAvatar, name="ajax_getUserAvatar"),
    path('ajax/checkEmailIntegrity/', Views.CheckEmailIntegrity, name="ajax_checkEmailIntegrity"),
    path('ajax/checkPhoneIntegrity/', Views.CheckTelIntegrity, name="ajax_checkTelIntegrity"),
    path('ajax/checkStudentIdIntegrity/', Views.CheckStudentIdIntegrity, name="ajax_checkStudentIdIntegrity"),
    path('ajax/userlookup/', Views.UserLookup.as_view(), name="ajax_userLookup"),
    path('ajax/prize/get_pool/<str:id>/', LuckyDrawDataView.as_view(), name="luckydrawget"),
]
