from django.db import models
from django.urls import reverse
import uuid
from UserAuthAPI import models as userModel
# Create your models here.

class Prize(models.Model):
    '''
    Prize Model Class - New active user win prize
    '''
    id = models.AutoField(primary_key=True, editable= False)
    prize_name=models.CharField(max_length=30)
    prize_UserId=models.ForeignKey(userModel.UserProfile, on_delete=models.DO_NOTHING)