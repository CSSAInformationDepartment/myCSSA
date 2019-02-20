
###############################################################################
#                    Desinged & Managed by Josh.Le.LU                         #
#                                                                             #
#                     █████╗ ██╗     ██╗ ██████╗███████╗                      #
#                    ██╔══██╗██║     ██║██╔════╝██╔════╝                      #
#                    ███████║██║     ██║██║     █████╗                        #
#                    ██╔══██║██║     ██║██║     ██╔══╝                        #
#                    ██║  ██║███████╗██║╚██████╗███████╗                      #
#                    ╚═╝  ╚═╝╚══════╝╚═╝ ╚═════╝╚══════╝                      #
#        An agile web application platform bulit on top of Python/django      #
#                                                                             #
#                Proprietary version made for myCSSA project                  #
#                             Version: 0.6a(C)                                #
#                                                                             #
###############################################################################


# Create your models here.
from django.db import models
from django.core.validators import MaxValueValidator
import uuid
from django.utils.translation import ugettext_lazy as _

from UserAuthAPI import models as adminModel
from BlogAPI import models as BlogModel

# Create your models here.
# 此为myCSSA活动管理模型

############# 模型编写规则 ##############
# 1. 使用驼峰命名法
# 2. 对象名首字母大写
# 3. 变量名首字母小写
# 4. 其余格式说明请见代码区 (adminHub/models.py)
# 5. 为每个模型编写序列化类, ID类字段必须设为只读 (serlizers.py)

#######################################
## 官方教程：https://docs.djangoproject.com/en/2.1/intro/tutorial02/

class EventUndertaker (models.Model):
    eventTakerId = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    eventTakerName = models.CharField(max_length = 50)

    def __str__(self):
        return self.eventTakerName

# contacter weak entity
class TakerContacter (models.Model):
    contacterId = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    contacterName = models.CharField(max_length = 50)
    eventTakerId = models.ForeignKey(EventUndertaker, on_delete = models.CASCADE)
    contacterContact = models.CharField(max_length = 50)

    def __str__(self):
        return self.contacterName

class EventType(models.Model):
    eventTypeId = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    typeName = models.CharField(max_length = 50)

    def __str__(self):
        return self.typeName

# Event本身
class Event (models.Model):
    eventID = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    eventName = models.CharField(verbose_name=_("活动名称"), max_length = 50, unique=True)
    eventInfo = models.CharField(verbose_name=_("活动简介"), max_length = 600)

    eventStartTime = models.DateTimeField(auto_now_add=True)
    eventSignUpTime = models.DateTimeField(verbose_name=_("报名开始时间"))
    eventActualStTime = models.DateTimeField(verbose_name=_("活动开始时间"))

    mainVisual = models.ImageField(verbose_name=_("主视觉图"),upload_to='uploads/usrImage/eventMainVisual',default=None ,null=True)
    
    hasMaxAttendent = models.BooleanField(verbose_name=_("是否有人数上限?"),default=False)
    maxAttendent = models.IntegerField(verbose_name=_("人数上限"), default=0, blank=True, validators=[MaxValueValidator(1000),])
    address = models.CharField(verbose_name=_("地址"), max_length=200, default=None, null=True)
    venue = models.CharField(verbose_name=_("场馆名称"), max_length=50, default=None, null=True)

    isMemberOnly = models.BooleanField(verbose_name=_("是否为CSSA会员限定活动?"), default=False)

    isFree = models.BooleanField(verbose_name=_("是否为免费活动?"), default=True)
    price = models.DecimalField(verbose_name=_("门票价格"), max_digits=10, decimal_places=2, default=0.0)

    # 活动主办方
    eventBy = models.ForeignKey(EventUndertaker, verbose_name=_("活动主办方"),on_delete=models.PROTECT)

    # 活动类型
    eventTypes = models.ForeignKey(EventType, verbose_name=_("活动类型"), on_delete=models.DO_NOTHING)

    # 相关推文
    relatedArticles = models.ForeignKey(BlogModel.Blog, verbose_name=_("相关介绍文章"), on_delete=models.PROTECT, default=None)

    disabled = models.BooleanField(default=False)

    def __str__(self):
        return self.eventName

# UserProfile 参加 Event 的多对多 association entity
class AttendEvent (models.Model):

    attendedId = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    attendedEventId = models.ForeignKey(Event, on_delete = models.CASCADE)
    attendedUserId = models.ForeignKey(adminModel.User, on_delete = models.DO_NOTHING)

    # 交费及评价
    paid = models.BooleanField
    comment = models.CharField(max_length = 150)
