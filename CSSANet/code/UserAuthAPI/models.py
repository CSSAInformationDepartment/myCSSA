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


from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
import uuid
from django.utils.translation import ugettext_lazy as _

from django.conf import settings
from django.contrib.auth import get_user_model

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

## 自定义用户管理
class UserManager(BaseUserManager):

    use_in_migrations = True

    def create_user(self, email, telNumber, password=None):
        user = self.model(
            email=self.normalize_email(email),
            telNumber=telNumber,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, telNumber, password):
        user = self.create_user(
            email,
            password=password,
            telNumber=telNumber,
        )
        user.is_staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, telNumber, password):
        user = self.create_user(
            email=email,
            password=password,
            telNumber=telNumber,
        )
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user




##### Part 1. 用户信息扩展数据 ##################################################
#部门 (对应fixture)
class CSSADept (models.Model):
    # 此行定义表主键 - 标准写法，请复制粘贴
    deptId = models.AutoField(primary_key = True, editable=False)
    deptName = models.CharField(max_length=50, verbose_name="部门简称")
    deptTitle = models.CharField(max_length=50, verbose_name="部门名称")
    deptTitleEN = models.CharField(max_length=50, verbose_name="Name of the Department")

    def __str__(self):
        return self.deptName

#职位 (对应fixture)
class CSSARole (models.Model):
    roleId = models.AutoField(primary_key=True, editable=False)
    roleFlag = models.CharField(max_length=3)
    roleName = models.CharField(max_length=50)

    def __str__(self):
        return '%s %s' % (self.roleFlag,self.roleName)

#学校专业信息
class UniMajor (models.Model):
    uniMajorId = models.AutoField(primary_key=True, editable=False)
    majorName = models.CharField(max_length=100)

    def __str__(self):
        return self.majorName

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None
    email = models.CharField(verbose_name="电子邮箱",max_length = 100,unique=True)
    telNumber = models.CharField(verbose_name="联系电话", max_length = 16, default='0400000000')

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('telNumber',)

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return '%s' % (self.email)

    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        '''
        Returns the short name for the user.
        '''
        return self.first_name

#    def email_user(self, subject, message, from_email=None, **kwargs):
#        '''
#        Sends an email to this User.
#        '''
#        send_mail(subject, message, from_email, [self.email], **kwargs)


#用户信息主体 （继承自标准admin model，参照： https://www.zmrenwu.com/post/31/）
class UserProfile (models.Model):
    user = models.OneToOneField(User,on_delete=models.DO_NOTHING, primary_key=True, blank=True)

    avatar = models.ImageField(verbose_name="头像", upload_to=_GetUserDir,
    height_field=None, width_field=None, max_length=None,null=True, blank=True)

    infocardBg = models.ImageField(verbose_name="名片背景",upload_to=_GetUserDir,
    height_field=None, width_field=None, max_length=None,null=True, blank=True)

    identiyConfirmed = models.BooleanField(verbose_name="会员身份状态",default=False)
    isValid = models.BooleanField(verbose_name="账号有效性",default=False)

    firstNameEN = models.CharField(verbose_name="英文名",max_length=50)
    lastNameEN = models.CharField(verbose_name="英文姓",max_length=50)

    firstNameCN = models.CharField(verbose_name="中文名",max_length=50,null=True, blank=True)
    lastNameCN = models.CharField(verbose_name="中文姓",max_length=50,null=True, blank=True)

    genderChoice = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    )
    gender = models.CharField(choices = genderChoice,default='Other',max_length=50)

    dateOfBirth = models.DateField(verbose_name="生日", null=True)
    joinDate = models.DateTimeField(auto_now_add=True)
    studentId = models.CharField(verbose_name="学生证号",max_length=10)
    membershipId = models.CharField(verbose_name="会员卡号", max_length=10,null=True, blank=True)


    address = models.CharField(verbose_name="地址",max_length=150, null=True)
    postcode = models.CharField(verbose_name="邮编",max_length=4, null=True)
    originate = models.CharField(verbose_name="籍贯",max_length=50, null=True)



class CSSACommitteProfile(models.Model):
    Id = models.AutoField(primary_key=True, editable=False)
    member = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    is_active = models.BooleanField(default=False)
    CommenceDate = models.DateTimeField(auto_now_add=True)
    Department = models.ForeignKey(CSSADept, on_delete=models.DO_NOTHING)



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

    academicRecId = models.AutoField(primary_key=True, editable=False)
    # 来自同一张表的外键变量名、配置需一致
    userProfile = models.ForeignKey(User, on_delete = models.DO_NOTHING, blank=True)
    # 不同模型中表示同一功能的变量名需一致
    timeOfCreate  = models.DateTimeField(auto_now_add=True)

    degree = models.CharField(verbose_name="学位", choices=degreeChoice,
        max_length=32, default='BA')
    uniMajor = models.CharField(verbose_name="专业" ,max_length=100)
