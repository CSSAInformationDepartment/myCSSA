from django.contrib import admin
from .models import Resume,JobList

# Register your models here.

admin.site.register(JobList)
admin.site.register(Resume)