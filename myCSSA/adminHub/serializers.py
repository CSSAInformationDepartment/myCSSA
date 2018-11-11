from rest_framework import serializers
from adminHub import models as AdminModels

class MessageListSerializers(serializers.ModelSerializer):
    fields = ('messageId', 'repliedId', 'messageTitle', 'timeOfSend', '')
