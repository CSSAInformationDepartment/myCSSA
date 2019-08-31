from rest_framework import serializers
from .models import JobList 
from UserAuthAPI.models import User, UserProfile

class JobListSerializers(serializers.ModelSerializer):
    detail_url = serializers.SerializerMethodField()
    
    def get_detail_url(self, obj):
        return obj.get_absolute_url() # return the absolute url of the object

    class Meta:
        model = JobList
        fields = ('jobID', 'jobName', 'dept', 'dueDate','detail_url') #organizationName? pagenation?
    
