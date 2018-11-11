from rest_framework import serializers
import events.models as EventModel

class EventUndertakerSerializers(serializers.ModelSerializer):
    class Meta:
        model = EventModel.EventUndertaker #对应的模型名称
        fields = '__all__' #对应的数据字段
        read_only_fields = ('eventTakerId',) #只读字段就算只有一个也必须在结尾加逗号


class EventTypeSerializers(serializers.ModelSerializer):
    class Meta:
        model = EventModel.EventType
        fields = '__all__'
        read_only_fields = ('eventTypeId',)

class EventSerializers(serializers.ModelSerializer):
    class Meta:
        model = EventModel.Event
        fields = '__all__'
        read_only_fields = ('eventID',)

class AttendEventSerializers(serializers.ModelSerializer):
    class Meta:
        model = EventModel.AttendEvent
        fields = '__all__'
