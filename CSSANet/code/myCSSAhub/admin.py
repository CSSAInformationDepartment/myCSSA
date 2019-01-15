from django.contrib import admin

from myCSSAhub import models

# Register your models here.
admin.site.register(models.Notification_DB)
admin.site.register(models.AccountMigration)
admin.site.register(models.EmailConfiguration)
admin.site.register(models.EmailDB)
admin.site.register(models.DiscountMerchant)
