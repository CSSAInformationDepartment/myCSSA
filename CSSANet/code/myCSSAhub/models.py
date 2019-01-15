from django.db import models
from UserAuthAPI import models as userModels
import uuid
import django.utils.timezone as timezone

# Create your models here.


class AppAccessControl(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    appName = models.CharField(max_length=500)
    is_accessible = models.BooleanField(default=False)


class Notification_DB(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    # 如果为all@cssa.com的特定ID,则代表群发
    status = models.IntegerField()
    sendID = models.ForeignKey(
        userModels.User, related_name="发送者id", on_delete=None)
    recID = models.ForeignKey(
        userModels.User, related_name="接受者id", on_delete=None)
    content = models.CharField(verbose_name="站内信内容", max_length=200, null=True)
    title = models.CharField(verbose_name="站内信标题", max_length=200, null=True)
    # 默认加入时间为写入数据库的时间
    add_date = models.DateTimeField(
        verbose_name="信息加入时间", default=timezone.now)


class AccountMigration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    time = models.DateField(auto_now_add=True)
    studentId = models.CharField(verbose_name="学生证号", max_length=10)
    membershipId = models.CharField(verbose_name="会员卡号", max_length=10)


class EmailConfiguration(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    host_password = models.CharField(
        verbose_name="发送方密码", max_length=200, null=True)
    host_user = models.CharField(
        verbose_name="发送方用户", max_length=200, null=True)
    port = models.IntegerField(verbose_name="端口")


class EmailDB(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    # 如果为all@cssa.com的特定ID,则代表群发
    sendID = models.ForeignKey(
        userModels.User, related_name="发信者id", on_delete=None)
    recID = models.ForeignKey(
        userModels.User, related_name="接信者id", on_delete=None)
    content = models.CharField(verbose_name="email内容", max_length=200, null=True)
    title = models.CharField(verbose_name="email标题", max_length=200, null=True)
    # 默认加入时间为写入数据库的时间
    add_date = models.DateTimeField(
        verbose_name="信息加入时间", default=timezone.now)

class DiscountMerchant(models.Model):
    merchant_id = models.AutoField(primary_key=True, editable=False) 
    merchant_name =  models.CharField(verbose_name="商家名", max_length=200, null=True)
    merchant_description =  models.CharField(verbose_name="商家介绍", max_length=200, null=True)
    merchant_phone =  models.CharField(verbose_name="联系电话", max_length=200, null=True)
    merchant_address =  models.CharField(verbose_name="商家地址", max_length=200, null=True)
    merchant_link =  models.CharField(verbose_name="商家网站", max_length=200, null=True)
    merchant_add_date = models.DateTimeField(verbose_name="商户加入时间", default=timezone.now)
    merchant_image =  models.ImageField(upload_to = 'img/merchants/', default = 'img/merchants/noneImg.jpg')
   