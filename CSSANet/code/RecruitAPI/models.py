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
from UserAuthAPI import models as adminModel
import uuid
# Create your models here
#

#岗位列表
class JobList(models.Model):
    jobId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dept = models.ForeignKey(adminModel.CSSADept,verbose_name="部门", on_delete=models.CASCADE)
    timeOfCreate = models.DateTimeField(auto_now_add=True)
    jobName = models.CharField(verbose_name="职位名称", max_length=50, default=None)
    description = models.CharField(verbose_name="职位介绍", max_length=400, default=None)
    dueDate = models.DateTimeField(verbose_name="截止日期", default=None, null=True)

class Resume(models.Model):
    CVId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    jobRelated = models.ForeignKey(JobList,verbose_name="相应职位", on_delete=models.CASCADE)
    user = models.ForeignKey(adminModel.User, on_delete=models.DO_NOTHING, default=None, blank=True, null=True)

    reason = models.CharField(verbose_name="申请原因", max_length=400, default=None)
    hobby = models.CharField(verbose_name="兴趣爱好", max_length=400, default=None)
    eduBackground = models.CharField(verbose_name="教育背景", max_length=400, default=None, blank=True, null=True)
    inSchoolExp = models.CharField(verbose_name="校内经历", max_length=400, default=None)
    outSchoolExp = models.CharField(verbose_name="校外经历", max_length=400, default=None, blank=True, null=True)
    additionMsg = models.CharField(max_length=400, default=None, blank=True, null=True)

    isOpened = models.BooleanField(default=False, blank=True, null=True)
    isEnrolled = models.BooleanField(default=False, blank= True, null=True)
    isOfferd = models.BooleanField(default=False, blank=True, null=True)
    isReject = models.BooleanField(default=None, blank=True, null=True)


# 可能以后要并入认识管理模块
#class UserAccComment (models.Model):
#    accCommentId = models.UUIDField(primary_key=True, default=uuid.uuid4,
#        editable=False)
#    timeOfCreate = models.DateTimeField(auto_now_add=True)
#    userProfile = models.ForeignKey(UserProfile, verbose_name="用户",
#        on_delete=models.CASCADE)
#    comment = models.CharField(verbose_name="备注", max_length=200)
