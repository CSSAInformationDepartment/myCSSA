
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
    path('regform/', Views.register_form , name='hub_regform'),
]
