from django.db import models
from UserAuthAPI import models as UserModel
from EventAPI import models as EventModels
# Create your models here.

class Prize(models.Model):
    '''
    Prize Model Class - New active user win prize
    '''
    id = models.AutoField(primary_key=True, editable= False)
    prize_name=models.CharField(max_length=30)
    prize_userId=models.ForeignKey(UserModel.UserProfile, on_delete=models.DO_NOTHING)



class PrizePool(models.Model):
    '''
    Prize Model Class - contains all candidates in the model
    '''

    id = models.AutoField(primary_key=True, editable=False)
    user = models.ForeignKey(UserModel.UserProfile, on_delete=models.CASCADE)
    event_related = models.ForeignKey(EventModels.Event, on_delete=models.CASCADE, null=True, default=None)
    group_tag = models.CharField(max_length=250)


    
    