from django.contrib import admin

from CommunityAPI.models import Tag, Post, Report, Content

# Register your models here.

admin.site.register(Tag)
admin.site.register(Post)
admin.site.register(Report)
admin.site.register(Content)
