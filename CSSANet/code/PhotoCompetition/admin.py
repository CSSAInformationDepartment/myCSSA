from django.contrib import admin
from . import models
# Register your models here.



admin.site.register(models.Submission)
admin.site.register(models.ApprovedSubmission)
admin.site.register(models.SubmissionVoting)