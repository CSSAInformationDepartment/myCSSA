from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.utils.translation import ugettext_lazy as _

from UserAuthAPI import models
# Register your models here.

#@admin.register(User)
class CsutomUserAdmin(UserAdmin):
    """Define admin model for custom User model with no email field."""

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name','telNumber')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 
                                    'is_council_member','is_business_account',
                                    'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'id','is_active','is_staff', 'is_superuser', 'is_council_member','is_business_account',)
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user','firstNameEN','lastNameEN','gender','dateOfBirth' ,'membershipId',)
    list_display_links = ('user',)
    search_fields = ('lastNameEN','firstNameEN','user__email','user__telNumber','studentId','membershipId')
    list_per_page = 25

class CommitteeAdmin(admin.ModelAdmin):
    list_display = ('Id','member','is_active','Department','role','CommenceDate')
    list_display_links = ('Id',)
    search_fields = ('member__firstNameEN','member__lastNameEN','Department__deptTitle','role__roleName')
    list_per_page = 25


admin.site.register(models.User, CsutomUserAdmin)
admin.site.register(models.UniMajor)
admin.site.register(models.CSSADept)
admin.site.register(models.CSSARole)
admin.site.register(models.UserProfile, UserProfileAdmin)

admin.site.register(models.UserAcademic)

admin.site.register(models.CSSACommitteProfile, CommitteeAdmin)