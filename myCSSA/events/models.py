from django.db import models
import uuid

# import userprofile class 但是应该是有问题的
from adminHub import models as adminModel

# Create your models here.
# 此为myCSSA活动管理模型

############# 模型编写规则 ##############
# 1. 使用驼峰命名法
# 2. 对象名首字母大写
# 3. 变量名首字母小写
# 4. 其余格式说明请见代码区 (adminHub/models.py)
#######################################
## 官方教程：https://docs.djangoproject.com/en/2.1/intro/tutorial02/

class EventUndertaker (models.Model):
    eventTakerId = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    eventTakerName = models.CharField(max_length = 50)


# contacter weak entity
class TakerContacter (models.Model):
    contacterId = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    contacterName = models.CharField(max_length = 50)
    eventTakerId = models.ForeignKey(EventUndertaker, on_delete = models.CASCADE)
    contacterContact = models.CharField(max_length = 50)

class eventType(models.Model):
    eventTypeId = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    typeName = models.CharField(max_length = 50)

# Event本身
class Event (models.Model):
    eventID = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    eventName = models.CharField(max_length = 50)
    eventInfo = models.CharField(max_length = 600)

    eventStartTime = models.DateTimeField(auto_now_add=True)
    eventSignUpTime = models.DateTimeField()
    eventActualStTime = models.DateTimeField()

    # 活动主办方，
    eventBy = models.ForeignKey(EventUndertaker,on_delete=models.PROTECT)

    #活动类型
    eventTypes = models.ForeignKey(eventType,on_delete=models.DO_NOTHING)


# UserProfile 参加 Event 的多对多 association entity
class AttendEvent (models.Model):

    attendedId = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    attendedEventId = models.ForeignKey(Event, on_delete = models.CASCADE)
    attendedUserId = models.ForeignKey(adminModel.UserProfile, on_delete = models.DO_NOTHING)

    # 交费及评价
    paid = models.BooleanField
    comment = models.CharField(max_length = 150)


