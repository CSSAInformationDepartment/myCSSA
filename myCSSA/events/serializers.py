
from rest_framework import serializers
import events.models

class EventUndertakerSerializers(serializers.ModelSerializer):
    class Meta:
        model = EventUndertaker #对应的模型名称
        fields = ('eventTakerId', 'eventTakerName') #对应的数据字段
        read_only_fields = ('eventTakerId')


class EventType(serializers.ModelSerializer):
    class Meta:
        model = EventType
        fields = ('eventTypeId', 'typeName')
        read_only_fields = ('eventTypeId')

class Event(serlizers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('eventID', 'eventName' , 'eventInfo', 'eventStartTime',
        'eventSignUpTime', 'eventActualStTime', 'eventBy', 'eventTypes')
        read_only_fields = ('eventID')

class AttendEvent(serlizers.ModelSerializer):
    class Meta:
        model = AttendEvent
        fields = ('attendedId','attendedEventId', 'attendedUserId')


    """docstring for AttendEvent."""
    def __init__(self, arg):
        super(AttendEvent, self).__init__()
        self.arg = arg
