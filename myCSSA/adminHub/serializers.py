from rest_framework import serializers
from adminHub import models as AdminModels

class MessageListSerializers(serializers.ModelSerializer):
    class Meta:
        fields = ('messageId', 'repliedId', 'messageTitle', 'timeOfSend', 'isRead',
        'isDraft','sender','receiver')
        read_only_fields = ('messageId', 'repliedId')


class  MessageBodySerializers(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
