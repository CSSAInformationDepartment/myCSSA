from django.contrib import admin
from django.urls import path, re_path, include
from PublicSite import views as Views
from django.conf.urls import handler400, handler403, handler404, handler500

urlpatterns = [
    path('', Views.index, name='PublicSite'),
    path('news/',Views.News, name='News'),
    re_path(r'^department/(?P<dept>[\w-]+)/$', Views.Departments, name='departments-page'),
]


################################# errors pages testing########################################
#urlpatterns += [
#     path('400/', Views.bad_request, name='bad_request'),
#     path('403/', Views.permission_denied, name='permission_denied'),
#     path('404/', Views.page_not_found, name='page_not_found'),
#     path('500/', Views.server_error, name='server_error')
# ]    
################################# errors pages testing########################################
handler400 = Views.bad_request
handler403 = Views.permission_denied
handler404 = Views.page_not_found
handler500 = Views.server_error

