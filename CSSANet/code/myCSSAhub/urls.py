
from django.urls import path
from myCSSAhub import views as Views

app_name = "myCSSAhub"
urlpatterns = [
    path('home/', Views.home, name="home"),
    path('userinfo/', Views.userInfo, name="userInfo"),
    path('message/', Views.message, name="message"),
    path('notifications/', Views.notifications, name="notifications"),
    path('login/', Views.login_page, name="hub_login"),
    path('logout/', Views.logout_page , name='hub_logout'),
    path('register/', Views.register_guide , name='hub_reg'),
    path('regform/', Views.register_form , name='hub_regform')
]


################################# errors pages testing########################################
urlpatterns += [
     path('400/', Views.bad_request, name='bad_request'),
#     path('403/', Views.permission_denied, name='permission_denied'),
#     path('404/', Views.page_not_found, name='page_not_found'),
#     path('500/', Views.server_error, name='server_error')
]     
################################# errors pages testing########################################

handler400 = Views.bad_request
handler403 = Views.permission_denied
handler404 = Views.page_not_found
handler500 = Views.server_error