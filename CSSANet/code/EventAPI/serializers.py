from rest_framework import serializers
from . import models as EventModels


class NewEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventModels.Event
        fields = '__all__'
        exclude = ('DisplayArticleType',)

    