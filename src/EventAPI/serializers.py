from rest_framework import serializers
from EventAPI.models import Event as eventModels

class EventsSerializer(serializers.ModelSerializer):

    class Meta:
      model = eventModels

      fields = ('eventID','eventName','eventInfo','mainVisual','address','venue','isFree','price',
                'eventBy','eventTypes')
      