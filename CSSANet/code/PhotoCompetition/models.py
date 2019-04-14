from django.db import models
from UserAuthAPI import models as adminModel

# Create your models here.
class FilesSubmission(models.Model):
    id = models.AutoField(primary_key = True, editable = False)
    submission_id = models.ForeignKey(submission.Id, on_delete = models.Do_NOTHING)
    submission_user=models.ForeignKey(adminModel.User, on_delete=models.DO_NOTHING)
    upload_photo = models.FileField(default=None, null=True, blank=True, upload_to='competition/competitionPics')
    Description = models.CharFiled(max_length = 250)