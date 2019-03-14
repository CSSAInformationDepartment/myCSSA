from django.db import models
from django.core.validators import MaxValueValidator
from UserAuthAPI import models as userModels
import uuid
import django.utils.timezone as timezone

# Create your models here.


class AppAccessControl(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    appName = models.CharField(max_length=500)
    is_accessible = models.BooleanField(default=False)





class AccountMigration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    time = models.DateField(auto_now_add=True)
    studentId = models.CharField(verbose_name="学生证号", max_length=10)
    membershipId = models.CharField(verbose_name="会员卡号", max_length=10)



class DiscountMerchant(models.Model):
    merchant_id = models.AutoField(primary_key=True, editable=False)
    merchant_name =  models.CharField(verbose_name="商家名", max_length=200, null=True)
    merchant_description =  models.TextField(verbose_name="商家介绍", null=True, blank=True, default=None)
    merchant_phone =  models.CharField(verbose_name="联系电话", max_length=200, null=True,blank=True)
    merchant_address =  models.CharField(verbose_name="商家地址", max_length=200, null=True)
    merchant_link =  models.CharField(verbose_name="商家网站", max_length=200, null=True,blank=True)
    merchant_add_date = models.DateTimeField(verbose_name="商户加入时间", default=timezone.now)
    merchant_image =  models.ImageField(upload_to = 'img/merchants/', default = 'img/merchants/noneImg.jpg')
    merchant_qrcode=models.ImageField(verbose_name="微信二维码",upload_to='uploads/usrImage/merchantWechatQRcode',default=None ,null=True, blank=True)
    merchantType = (
        ('折扣商家', '折扣商家'),
        ('赞助商家', '赞助商家'),
    )
    merchant_type = models.CharField(verbose_name="商户类型", max_length=10, choices= merchantType, null=True, default='折扣商家')
    merchantLevel = (
        ('无', '无'),
        ('钻石商家', '钻石商家'),
        ('金牌商家', '金牌商家'),
        ('银牌商家', '银牌商家'),
    )
    merchant_level = models.CharField(verbose_name="赞助商等级", max_length=10, choices= merchantLevel, null=True, default='银牌商家',blank=True)
    merchantCategory = (
        ('无', '无'),
        ('美食', '美食'),
        ('休闲娱乐', '休闲娱乐'),
        ('便捷生活', '便捷生活'),
    )
    merchant_Category = models.CharField(verbose_name="折扣商家种类", max_length=10, choices= merchantCategory, null=True, default='美食',blank=True)

    def __str__(self):
        return self.merchant_name

    def get_absolute_url(self):
        return reverse("myCSSAhub:merchant_profile", args=[str(self.merchant_id)])
