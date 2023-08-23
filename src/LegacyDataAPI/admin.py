from django.contrib import admin

from LegacyDataAPI import models


class LegacyUsersAdmin(admin.ModelAdmin):
    list_display = ('recordId', 'email', 'firstNameEN', 'lastNameEN',
                    'dateOfBirth', 'joinDate', 'studentId', 'membershipId')
    list_display_links = ('recordId',)
    search_fields = ('email', 'firstNameEN', 'lastNameEN',
                     'dateOfBirth', 'joinDate', 'studentId', 'membershipId')
    list_per_page = 50


# Register your models here.
admin.site.register(models.LegacyUsers, LegacyUsersAdmin)
