from . import models
from rest_framework import serializers

class JoblistAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.JobList
        fields = ['jobName', 'disabled']