from django.db import models
from adminHub import models as adminModel
# Create your models here
# 

#岗位列表
def JobList(models.Model):
    jobId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dept = models.ForeignKey(adminModel.CSSADept,verbose_name="部门", on_delete=models.CASCADE)

    timeOfCreate = models.DateTimeField(auto_now_add=True)
    jobName = models.CharField(verbose_name="职位名称", max_length = 50, default = None)
    description = models.CharField(verbose_name="职位介绍", max_length = 400, default = None)
    dueDate = models.DateTimeField(verbose_name="截止日期")


def Resume(models.Model):
    CVId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    jobRelated = models.ForeignKey(JobList,verbose_name="相应职位", on_delete=models.CASCADE)
    
    reason = models.CharField(verbose_name="申请原因", max_length = 400, default = None)
    hobby = models.CharField(verbose_name="兴趣爱好", max_length = 400, default = None)
    eduBackground = models.CharField(verbose_name="教育背景", max_length = 400, default = None)
    inSchoolExp = models.CharField(verbose_name="校内经历", max_length = 400, default = None)
    outSchoolExp = models.CharField(verbose_name="校外经历", max_length = 400, default = None)

    isOpened = models.BooleanField(default=False)
    isEnrolled = models.BooleanField(default=False)
    isOfferd = models.BooleanField(default=False)
    
