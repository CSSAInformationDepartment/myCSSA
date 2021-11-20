from rest_framework import serializers
from EventAPI.models import Event as eventModels

class EventsSerializer(serializers.ModelSerializer):

    def get_eventTaker(self, instance):
        return instance.eventBy.eventTakerName if instance.eventBy else None

    def get_eventType(self, instance):
        return instance.eventTypes.typeName if instance.eventTypes else None

    class Meta:
      model = eventModels
      fields = ('eventID','eventName','eventInfo','mainVisual','address','venue','isFree','price',
                'pastEventLink', 'pastEventPoster', 'recentEventLink', 'recentEventPoster',)
      