from django.contrib import admin
from .models import HttpAccessLogModel
# Register your models here.
class HttpAccessLogAdmin(admin.ModelAdmin):
    list_display = ('id','time_stamp','visitor_ipv4','request_path','request_query_string','request_method','status_code','is_anonymous','user',)
    search_fields = ('visitor_ipv4', 'request_path', 'request_method')
    list_per_page = 50


admin.site.register(HttpAccessLogModel, HttpAccessLogAdmin)