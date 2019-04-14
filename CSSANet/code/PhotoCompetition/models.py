from django.db import models
from django.core.validators import MaxValueValidator
import uuid
from django.utils.translation import ugettext_lazy as _

from UserAuthAPI import models as adminModel

# Create your models here.
class Submission(models.Models):
    submissionId=models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    submissionUserId=models.ForeignKey(adminModel.User, on_delete=models.DO_NOTHING)
    submissionTime=models.DateTimeField(auto_now_add=True)
    DeviceChoice=(
        ('MobilePhone','手机'),
        ('Camera','相机'),
    )
    CategoryChoice=(
        ('Nature','风景'),
        ('Culture','人文'),
    )
    deviceType=models.CharField(verbose_name=_("设备"),choices=DeviceChoice, max_length=30, default="手机", null=True)
    categoryType=models.CharField(verbose_name=_("类别"), choices=CategoryChoice, max_length=30, default="风景", null=True)
    
class FilesSubmission(models.Model):
    id = models.AutoField(primary_key = True, editable = False)
    submission_id = models.ForeignKey(Submission, on_delete = models.CASCADE)
    submission_user=models.ForeignKey(adminModel.User, on_delete=models.DO_NOTHING)
    upload_photo = models.FileField(default=None, null=True, blank=True, upload_to='competition/competitionPics')
    Description = models.CharField(max_length = 250)
