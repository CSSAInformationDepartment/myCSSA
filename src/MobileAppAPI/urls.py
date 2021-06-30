# @File    : urls.py.py
# @Time    : 11/5/21 4:17 下午
# @Author  : Tianzhi Li
# @Email   : tianzhipengfei@gmail.com
# @Software: PyCharm

from django.urls import path
from MobileAppAPI import views as Views

app_name = "MobileAppAPI"
urlpatterns = [
    path('get_merchants/', Views.Merchants, name="get_merchants"),
    path('get_sponsors/', Views.Sponsors, name="get_sponsers"),
    path('update_merchants/', Views.UpdateMerchants, name="update_merchants"),
    # path('update_sponsors/', Views.UpdateSponsors, name="update_sponsers")
]