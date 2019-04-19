from django.contrib import admin
from PublicSite import models
# Register your models here.

class HomepageCarouselAdmin(admin.ModelAdmin):
    list_display = ('id','url','filePath','header','description')
    list_display_links = ('id',)
    search_fields = ('id',)
    list_per_page = 5



admin.site.register(models.HTMLFields)
admin.site.register(models.ImgAttributes)
admin.site.register(models.PageRegister)
admin.site.register(models.HomepageCarousels, HomepageCarouselAdmin)