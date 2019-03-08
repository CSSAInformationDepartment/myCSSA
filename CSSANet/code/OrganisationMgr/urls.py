
from django.urls import path, re_path, include
from OrganisationMgr import views


app_name = "OrganisationMgr"
urlpatterns = [
    path('deptmgr/', views.DepartmentManagementView.as_view(), name="dept_management"),

    path('member/', views.MemberListView.as_view(), name="member_list"),
    path('member/<str:id>/update/', views.UserProfileEditView.as_view(), name="update_member"),
    path('new_member/', views.MemberSearchView.as_view(), name='new_member'),
    path('new_member/<str:id>/detail/', views.MembershipActivationView.as_view(), name='new_member_activation'),
    path('new_member/<str:id>/result/', views.ConfirmActivationView.as_view(), name='confirm_activation'),
   #path('member/<str:id>/assign', views.)
]


## Internal AJAX path
urlpatterns += [
    
]