
from django.urls import path, re_path, include
from OrganisationMgr import views


app_name = "OrganisationMgr"
urlpatterns = [
    path('deptmgr/',views.DepartmentManagementView.as_view(), name="dept_management")
]


## Internal AJAX path
urlpatterns += [
    
]