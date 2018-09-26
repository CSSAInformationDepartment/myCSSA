from django.db import models
from django.contrib.auth.models import User, AbstractUser
from uuid import UUID, uuid4

# Create your models here.
# 此为myCSSA用户信息管理模型

############# 模型编写规则 ##############
# 1. 使用驼峰命名法
# 2. 对象名首字母大写
# 3. 变量名首字母小写
# 4. 其余格式说明请见代码区
#######################################
## 官方教程：https://docs.djangoproject.com/en/2.1/intro/tutorial02/

##### Part 1. 用户信息扩展数据 ######################################################
#部门
class CSSADept (models.Model):
    # 此行定义表主键
    deptId = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    deptName = models.CharField(max_length=50)


#职位
class CSSARole (models.Model):
    roleId = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    roleName = models.CharField(max_length=32)

#学校专业信息
class uniMajor (models.Model):
    uniMajorId = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    majorName = models.CharField(max_length=100)

#用户信息主体
class UserProfile (models.Model):
    identiyConfirmed = models.BooleanField
    isActivate = models.BooleanField

    usrName = models.CharField(max_length = 50)
    firstName = models.CharField(max_length = 50)
    lastName = models.CharField(max_length = 50)
    genderChoice = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    )

    gender = models.CharField(choices = genderChoice, max_length=50)
    joinDate = models.DateTimeField()
    student = models.CharField(max_length = 6)
    membershipId = models.CharField(max_length = 6)

#用户联系方式
class UserContact (models.Model):
    # 此行代表【联系方式】与【用户信息主体】为多对一关系， 
    # CASCADE参数表示当【主体】信息被删除时，所有相关的【联系方式】也会被删除。
    userProfile = models.ForeignKey(UserProfile, on_delete = models.CASCADE)
    
    timeOfCreate  = models.DateTimeField()
    telNumber = models.CharField(max_length = 12)
    email = models.CharField(max_length = 30)
    address = models.CharField(max_length = 100)
    postcode = models.CharField(max_length = 4)
    # >> 籍贯字段
    originate = models.CharField(max_length = 20) 

class UserAcademic (models.Model):
    academicRecId = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    # 来自同一张表的外键变量名、配置需一致
    userProfile = models.ForeignKey(UserProfile, on_delete = models.CASCADE)
    # 不同模型中表示同一功能的变量名需一致
    timeOfCreate  = models.DateTimeField()

