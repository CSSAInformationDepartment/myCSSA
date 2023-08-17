from rest_framework import serializers

from . import models


class JoblistAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.JobList
        fields = ['jobName', 'disabled']
