from django.db import models
from django.core.validators import MaxValueValidator
import uuid

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
        ('Culture','人文')，
    )
    deviceType=models.CharField(verbose_name=_("设备"),choices=DeviceChoice, max_length=30, default="手机", null=True)
    categoryType=models.CharField(verbose_name=_("类别"), choices=CategoryChoice, max_length=30, default="风景", null=True)
    
