from typing import Tuple
from django.contrib import admin
from . import models as PostmanModels
# Register your models here.

class MailDraftAdmin(admin.ModelAdmin):
    '''
    Django Admin Page settings for the MailDraft model
    '''
    list_display = ('id','author','date_created', 'date_updated', 'title', 'html_body', 'is_pure_text', 'disabled')
    list_display_links = ('id',)
    search_fields = ('title','author')
    list_per_page = 25 

class MailQueneAdmin(admin.ModelAdmin):
    '''
    Django Admin Page settings for the MailQuene model
    '''
    list_display = ('id','date_created','date_scheduled','mail_text','receiver','state','disabled',)
    list_display_links = ('id',)
    search_fields = ('mail_body','receiver')
    list_per_page = 25


admin.site.register(PostmanModels.MailQuene, MailQueneAdmin)
