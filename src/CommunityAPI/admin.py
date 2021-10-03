from django.contrib import admin
from sorl.thumbnail.admin import AdminImageMixin

from CommunityAPI.models import PostImage, Tag, Post, Report, Content, Notification


class SorlImageModelAdmin(AdminImageMixin, admin.ModelAdmin):
    pass


# Register your models here.

admin.site.register(Tag)
admin.site.register(Post)
admin.site.register(Report)
admin.site.register(Content)
admin.site.register(Notification)
admin.site.register(PostImage, SorlImageModelAdmin)
