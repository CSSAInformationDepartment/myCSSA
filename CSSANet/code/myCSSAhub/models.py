from django.db import models
from UserAuthAPI import models as userModels
import uuid

# Create your models here.


class AppAccessControl(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    appName = models.CharField(max_length=500)
    is_accessible = models.BooleanField(default=False)


class NotificationText (models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.CharField(verbose_name="站内信内容", max_length=200, null=True)


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # 如果为0则为所有人
    status = models.IntegerField()
    sendID = models.ForeignKey(userModels.User, related_name="发送者id", on_delete=None)
    recID = models.ForeignKey(userModels.User, related_name="接受者id", on_delete=None)
    messageID = models.ForeignKey(NotificationText, on_delete=None)
