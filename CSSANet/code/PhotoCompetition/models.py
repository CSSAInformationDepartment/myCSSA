from django.db import models
from django.urls import reverse
from django.core.validators import MaxValueValidator
import uuid
from django.utils.translation import ugettext_lazy as _
from sorl.thumbnail import ImageField as SorlImageField
from UserAuthAPI import models as adminModel

# Create your models here.
def _GetUserDir(instance, filename):
    return 'competition/competitionPics/user_{0}/{1}'.format(instance.submissionUserId.id, filename)

class Submission(models.Model):
    '''
    PhotoCompetition Model Class - Candidates Submission
    '''
    DEVICE_CHOICE=(
        ('MobilePhone','手机'),
        ('Camera','相机'),
    )
    CATEGORY_CHOICE=(
        ('Nature','风景'),
        ('Culture','人文'),
    )

    submissionId = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    submissionUserId = models.ForeignKey(adminModel.User, on_delete=models.DO_NOTHING)
    submissionTime = models.DateTimeField(auto_now_add=True)

    deviceType = models.CharField(verbose_name=_("设备类型"),choices=DEVICE_CHOICE, max_length=30, default="手机", null=True)
    categoryType = models.CharField(verbose_name=_("题材类型"), choices=CATEGORY_CHOICE, max_length=30, default="风景", null=True)
    upload_photo = SorlImageField(verbose_name=_("上传作品"), null=True, upload_to = _GetUserDir)
    description = models.CharField(verbose_name=_("作品简述"),max_length = 250)

    def get_absolute_url(self):
        return reverse("myCSSAhub:PhotoComp:submission-detail", kwargs={"pk": self.pk})
    


class ApprovedSubmission(models.Model):
    '''
    PhotoCompetition Model Class - Selected Submission to the next round

    '''
    id = models.AutoField(primary_key=True, editable=False)
    disabled  = models.BooleanField(default=False)
    submission = models.ForeignKey(Submission,verbose_name=_("作品") ,on_delete=models.CASCADE)
    aggregate_votes = models.IntegerField(verbose_name=_("获得票数"), default=0)
