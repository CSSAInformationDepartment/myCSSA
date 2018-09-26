from django.db import models
import uuid

# import userprofile class 但是应该是有问题的
from adminHub import models as adminModel

# Create your models here.
# 此为myCSSA用户信息管理模型

############# 模型编写规则 ##############
# 1. 使用驼峰命名法
# 2. 对象名首字母大写
# 3. 变量名首字母小写
# 4. 其余格式说明请见代码区 (adminHub/models.py)
#######################################
## 官方教程：https://docs.djangoproject.com/en/2.1/intro/tutorial02/

# Event本身
class Event (models.Model):
    eventID = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    eventName = models.CharField(max_length = 50)
    eventInfo = models.CharField(max_length = 100)

    eventStartTime = models.DateTimeField()
    eventSignUpTime = models.DateTimeField()
    eventActualStTime = models.DateTimeField()

    # 活动主办方，
    eventBy = models.CharField(max_length = 50)

    # event type, 只是例子..我都不知道有什么类型的活动
    MEETING = "meeting"
    LECTURE = "LECTURE"

    eventTypes = (
        (MEETING, "Meeting"),
        (LECTURE, "Lecture")    
    )

    eventTypes = models.CharField(choices = eventTypes)



# UserProfile 参加 Event 的多对多 association entity
class AttendEvent (models.Model):

    attendedEventId = models.ForeignKey(Event, on_delete = models.CASCADE, primary_key = True)

    # 引入UserProfile的foreign key 但是不知道行不行
    attendedUserId = models.ForeignKey(adminModel.UserProfile, on_delete = models.DO_NOTHING, primary_key = True)

    # 交费及评价
    paid = models.BooleanField
    comment = models.CharField(max_length = 150)


class EventUndertaker (models.Model):
    eventTakerId = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    eventTakerName = models.CharField(max_length = 50)


# contacter weak entity, 但我不知道这么写是不是对的
class TakerContacter (models.Model):
    contacterName = models.CharField(primary_key = True, max_length = 50)
    eventTakerId = models.ForeignKey(EventUndertaker, on_delete = models.CASCADE, primary_key = True)
    contacterContact = models.CharField(max_length = 50)


