
from django.urls import path
from adminHub import views as adminHub

app_name = "adminHub"
urlpatterns = [
    path('home/', adminHub.home, name="home"),
    path('userinfo/', adminHub.userInfo, name="userInfo"),
    path('message/', adminHub.message, name="message"),
    path('notifications/', adminHub.notifications, name="notifications"),
    path('login/', adminHub.login_page, name="hub_login"),
    path('logout/', adminHub.logout_page , name='hub_logout'),
]
