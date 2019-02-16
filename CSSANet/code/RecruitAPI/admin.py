from django.contrib import admin
from .models import Resume,JobList

class JobListAdmin(admin.ModelAdmin):
    list_display = ('jobId', 'dept', 'timeOfCreate', 'jobName', 'dueDate')
    list_display_links = ('jobId',)
    search_fields = ('jobId',)
    list_per_page = 25

class ResumeAdmin(admin.ModelAdmin):
    list_display = ('CVId','timeOfCreate', 'jobRelated', 'isOpened', 'isEnrolled', 'isOfferd', 'isReject')
    list_display_links = ('CVId',)
    search_fields = ('CVId',)
    list_per_page = 25


# Register your models here.

admin.site.register(JobList, JobListAdmin)
admin.site.register(Resume, ResumeAdmin)