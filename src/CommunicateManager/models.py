import django.utils.timezone as timezone
from django.db import models
from UserAuthAPI import models as userModels

# Create your models here.


class Notification_DB(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    # 如果为all@cssa.com的特定ID,则代表群发
    status = models.IntegerField()
    sendID = models.ForeignKey(
        userModels.User, related_name="发送者id", on_delete=models.DO_NOTHING)
    recID = models.ForeignKey(
        userModels.User, related_name="接受者id", on_delete=models.DO_NOTHING)
    content = models.CharField(verbose_name="站内信内容", max_length=200, null=True)
    title = models.CharField(verbose_name="站内信标题", max_length=200, null=True)
    # 默认加入时间为写入数据库的时间
    add_date = models.DateTimeField(
        verbose_name="信息加入时间", default=timezone.now)


class EmailDB(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    # 如果为all@cssa.com的特定ID,则代表群发
    sendID = models.ForeignKey(
        userModels.User, related_name="发信者id", on_delete=models.DO_NOTHING)
    recID = models.ForeignKey(
        userModels.User, related_name="接信者id", on_delete=models.DO_NOTHING)
    content = models.CharField(
        verbose_name="email内容", max_length=200, null=True)
    title = models.CharField(verbose_name="email标题", max_length=200, null=True)
    # 默认加入时间为写入数据库的时间
    add_date = models.DateTimeField(
        verbose_name="信息加入时间", default=timezone.now)


class EmailConfiguration(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    host_password = models.CharField(
        verbose_name="发送方密码", max_length=200, null=True)
    host_user = models.CharField(
        verbose_name="发送方用户", max_length=200, null=True)
    port = models.IntegerField(verbose_name="端口")
