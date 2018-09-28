from django.db import models
from django.contrib.auth.models import User, AbstractUser
import uuid

# Create your models here.
# 此为myCSSA用户信息管理模型

############# 模型编写规则 ##############
# 1. 使用驼峰命名法
# 2. 对象名首字母大写
# 3. 变量名首字母小写
# 4. 其余格式说明请见代码区
#######################################
## 官方教程：https://docs.djangoproject.com/en/2.1/intro/tutorial02/


## 用户文件路径函数
def _GetUserDir(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.id, filename)


##### Part 1. 用户信息扩展数据 ######################################################
#部门
class CSSADept (models.Model):
    # 此行定义表主键 - 标准写法，请复制粘贴
    deptId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    deptName = models.CharField(max_length=50)

    def __str__(self):
        return self.deptName


#职位
class CSSARole (models.Model):
    roleId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    roleName = models.CharField(max_length=32)

    def __str__(self):
        return self.roleName

#学校专业信息
class UniMajor (models.Model):
    uniMajorId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    majorName = models.CharField(max_length=100)

    def __str__(self):
        return self.majorName

#用户信息主体 （继承自标准admin model，参照： https://www.zmrenwu.com/post/31/）
class UserProfile (AbstractUser):
    REQUIRED_FIELDS=('identiyConfirmed','isActivate','firstNameEN','lastNameEN','studentId','membershipId','email')

    avatar = models.ImageField(verbose_name="头像", upload_to=_GetUserDir, height_field=None, width_field=None, max_length=None, null=True)
    infocardBg = models.ImageField(verbose_name="名片背景", upload_to=_GetUserDir, height_field=None, width_field=None, max_length=None, null=True)

    identiyConfirmed = models.BooleanField(verbose_name="会员身份状态",default=False)
    isValid = models.BooleanField(verbose_name="账号有效性",default=False)

    firstNameEN = models.CharField(verbose_name="英文名",max_length = 50)
    lastNameEN = models.CharField(verbose_name="英文姓",max_length = 50)
    firstNameCN = models.CharField(verbose_name="中文名", max_length = 50,null=True)
    lastNameCN = models.CharField(verbose_name="中文姓",max_length = 50,null=True)

    genderChoice = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    )
    gender = models.CharField(choices = genderChoice,default='O' ,max_length=50)

    dateOfBirth = models.DateTimeField(verbose_name="生日", null=True)
    joinDate = models.DateTimeField(auto_now_add=True)
    studentId = models.CharField(verbose_name="学生证号",max_length = 6)
    membershipId = models.CharField(verbose_name="会员卡号", max_length = 6,null=True)

    class Meta(AbstractUser.Meta):
        pass
    
    def __str__(self):
        return '%s %s' % (self.firstNameEN, self.lastNameEN)

#用户联系方式
class UserContact (models.Model):
    # 此行代表【联系方式】与【用户信息主体】为多对一关系， 
    # CASCADE参数表示当【主体】信息被删除时，所有相关的【联系方式】也会被删除。
    userProfile = models.ForeignKey(UserProfile, on_delete = models.CASCADE)
    
    timeOfCreate  = models.DateTimeField(auto_now_add=True)
    telNumber = models.CharField(verbose_name="联系电话",max_length = 12)
    email = models.CharField(verbose_name="电子邮箱",max_length = 30)
    address = models.CharField(verbose_name="地址",max_length = 100)
    postcode = models.CharField(verbose_name="邮编",max_length = 4)
    originate = models.CharField(verbose_name="籍贯",max_length = 20)


class UserAcademic (models.Model):
    degreeChoice = (
        ('CR', 'Certificate'),
        ('DP', 'Diploma'),
        ('FN', 'Foundation'),
        ('BA', 'Bachelor'),
        ('MA', 'Master'),
        ('JD', 'Jurum Doctor'),
        ('MD', 'Medical Doctor'),
        ('PhD', 'Doctor of Philosophy'),
    )

    academicRecId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # 来自同一张表的外键变量名、配置需一致
    userProfile = models.ForeignKey(UserProfile, on_delete = models.CASCADE)
    # 不同模型中表示同一功能的变量名需一致
    timeOfCreate  = models.DateTimeField(auto_now_add=True)
    degree = models.CharField(verbose_name="学位", choices=degreeChoice,max_length=32, default='BA')
    uniMajor = models.ForeignKey(UniMajor,verbose_name="专业" ,on_delete=None)
    
class UserAccComment (models.Model):
    accCommentId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timeOfCreate = models.DateTimeField(auto_now_add=True)
    userProfile = models.ForeignKey(UserProfile, verbose_name="用户", on_delete=models.CASCADE)
    comment = models.CharField(verbose_name="备注", max_length=200)



########### Part 2. 站内信相关 ###########################################

class adminMessage (models.Model):
    
    messageId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    repliedId = models.ForeignKey('self', on_delete=models.CASCADE, default=None)

    messageTitle = models.CharField(max_length = 50)
    timeOfCreate = models.DateTimeField(auto_now_add=True)
    timeOfSend = models.DateTimeField(null=True)
    isRead = models.BooleanField(default=False)
    isDraft = models.BooleanField(default=True)

    sender = models.ForeignKey(UserProfile, verbose_name="发件人", on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(UserProfile, verbose_name="收件人", on_delete=models.CASCADE, related_name='receiver')
    messageHTML = models.TextField(verbose_name="正文")
    

    class Meta:
        verbose_name = "信息"
        verbose_name_plural = "信息"

    def __str__(self):
        return self.messageTitle

    def get_absolute_url(self):
        return reverse("_detail", kwargs={"pk": self.pk})



########### Part 3. 任务流水 ###########################################
class adminTask (models.Model):
    diffcultyChoice = (
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5')
    )
    taskId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timeOfCreate = models.DateTimeField(auto_now_add=True)
    userProfile = models.ForeignKey(UserProfile, verbose_name="发起人", on_delete=models.CASCADE)

    taskName = models.CharField(verbose_name="任务名", max_length=50)
    taskDescription = models.CharField(verbose_name="任务描述", max_length=200)
    taskStart = models.DateTimeField(verbose_name="开始时间")
    taskEnd = models.DateTimeField(verbose_name="结束时间")
    difficulty = models.CharField(verbose_name="难度", choices=diffcultyChoice ,max_length=50)
    taskPoints = models.IntegerField(verbose_name="任务积分")

    class Meta:
        verbose_name = "任务"
        verbose_name_plural = "任务"

    def __str__(self):
        return self.taskName

    def get_absolute_url(self):
        return reverse("_detail", kwargs={"pk": self.pk})



class userTasks (models.Model):
    taskRecId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timeOfCreate = models.DateTimeField(auto_now_add=True)
    userProfile = models.ForeignKey(UserProfile, verbose_name="接受人", on_delete=models.CASCADE)
    task = models.ForeignKey(adminTask, verbose_name="任务", on_delete=models.CASCADE)
    isAccomplish = models.BooleanField(verbose_name="已完成", default=False)
    isCertified = models.BooleanField(verbose_name="已确认", default=False)