
from django.urls import path, re_path, include
from OrganisationMgr import views


app_name = "OrganisationMgr"
urlpatterns = [
    path('deptmgr/', views.DepartmentManagementView.as_view(), name="dept_management"),
    path('member/<str:id>/check', views.GetCommitteeDetail.as_view(), name="check_member"),
   #path('member/<str:id>/assign', views.)
]


## Internal AJAX path
urlpatterns += [
    
]