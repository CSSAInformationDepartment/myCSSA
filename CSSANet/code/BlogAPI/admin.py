from django.contrib import admin
from BlogAPI import models

# Register your models here.
admin.site.register(models.Blog)
admin.site.register(models.BlogOldContent)
admin.site.register(models.BlogWrittenBy)
admin.site.register(models.BlogTag)
admin.site.register(models.BlogInTag)
admin.site.register(models.BlogImage)
admin.site.register(models.BlogReviewed)
