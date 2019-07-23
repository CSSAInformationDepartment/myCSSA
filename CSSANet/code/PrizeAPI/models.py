from django.db import models
from UserAuthAPI import models as UserModel
# Create your models here.

class Prize(models.Model):
    '''
    Prize Model Class - New active user win prize
    '''
    id = models.AutoField(primary_key=True, editable= False)
    prize_name=models.CharField(max_length=30)
    prize_userId=models.ForeignKey(UserModel.UserProfile, on_delete=models.DO_NOTHING)
    