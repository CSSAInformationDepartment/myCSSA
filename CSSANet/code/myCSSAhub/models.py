from django.db import models
from UserAuthAPI import models as userModels
import uuid

# Create your models here.


class AppAccessControl(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    appName = models.CharField(max_length=500)
    is_accessible = models.BooleanField(default=False)

class Notification_DB(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    # 如果为0则为所有人
    status = models.IntegerField()
    sendID = models.ForeignKey(userModels.User, related_name="发送者id", on_delete=None)
    recID = models.ForeignKey(userModels.User, related_name="接受者id", on_delete=None)
    content = models.CharField(verbose_name="站内信内容", max_length=200, null=True)
    title = models.CharField(verbose_name="站内信标题", max_length=200, null=True)
