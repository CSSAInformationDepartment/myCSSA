# Create your models here.
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

############################  WARNING !!! #####################################
#                                                                             #
#    This part of code relates to the proprietary security features of        #
#                        myCSSA Account System                                #
#                                                                             #
#                                                                             #
#                          DO NOT DISCLOSE!                                   #
###############################################################################

from django.db import  models
import uuid

class LegacyUsers(models.Model):
    recordId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    identiyConfirmed = models.BooleanField(verbose_name="会员身份状态",default=False)
    isValid = models.BooleanField(verbose_name="账号有效性",default=False)
    isAdult = models.BooleanField(verbose_name="是否成年",default=False)
    
    firstNameEN = models.CharField(verbose_name="英文名",max_length = 50)
    lastNameEN = models.CharField(verbose_name="英文姓",max_length = 50)
    #NOTE：中文名非必须，其实可以考虑不存？
    firstNameCN = models.CharField(verbose_name="中文名", max_length = 50,null=True)
    lastNameCN = models.CharField(verbose_name="中文姓",max_length = 50,null=True)
    genderChoice = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    )
    gender = models.CharField(verbose_name="性别",choices = genderChoice,default='O' ,max_length=5)

    #日期格式统一 “YYYY-MM-DD”
    dateOfBirth = models.DateTimeField(verbose_name="生日", null=True)
    joinDate = models.DateTimeField(verbose_name="入会日期") #使用表单自动记录的取值，2018年的数据需要进行UNIX时间戳转换

    studentId = models.CharField(verbose_name="学生证号",max_length = 10) 
        #为确保未来扩展性，目前设置学生证号最大位宽10位，需要在前端代码中加以限制
    membershipId = models.CharField(verbose_name="会员卡号", max_length = 10,null=True)
        #为确保未来扩展性，目前设置会员卡号最大位宽10位，需要在前端代码中加以限制

    telNumber = models.CharField(verbose_name="联系电话",max_length = 12,null=True)
    email = models.CharField(verbose_name="电子邮箱",max_length = 30, null=True)
    address = models.CharField(verbose_name="地址",max_length = 100,null=True)
    postcode = models.CharField(verbose_name="邮编",max_length = 4,null=True)
    originate = models.CharField(verbose_name="籍贯",max_length = 20,null=True)
    majorName = models.CharField(verbose_name="专业",max_length=100,null=True)

    def __str__(self):
        return '%s %s %s' % (self.membershipId,self.firstNameEN, self.lastNameEN)

