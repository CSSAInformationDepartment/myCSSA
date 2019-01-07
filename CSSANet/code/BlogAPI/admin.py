from django.contrib import admin
from BlogAPI import models

# Register your models here.
admin.site.register(models.BlogDescription)
admin.site.register(models.BlogContent)
admin.site.register(models.BlogWrittenBy)
admin.site.register(models.BlogTag)
admin.site.register(models.BlogInTag)