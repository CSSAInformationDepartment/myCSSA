from rest_framework import serializers
from .models import JobList 
from UserAuthAPI.models import User, UserProfile

class JobListSerializers(serializers.ModelSerializer):
    # detail_url = serializers.SerializerMethodField()
    
    # return the absolute url of the object
    # def get_detail_url(self, obj):
    #     return obj.get_absolute_url() 

    class Meta:
        model = JobList
        fields = ('jobId', 'jobName', 'dueDate') #organizationName? pagenation?
    
