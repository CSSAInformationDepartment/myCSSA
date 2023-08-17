from django.contrib import admin

from .models import *

# Register your models here.

admin.site.register(Notification_DB)
admin.site.register(EmailConfiguration)
admin.site.register(EmailDB)
