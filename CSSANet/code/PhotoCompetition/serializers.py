from rest_framework import serializers
from .models import Submission, ApprovedSubmission
from UserAuthAPI.models import User


class SubmissionListSerializers(serializers.ModelSerializer):
    detail_url = serializers.SerializerMethodField()
    
    def get_detail_url(self, obj):
        return obj.get_absolute_url() # return the absolute url of the object

    class Meta:
        model = Submission
        fields = ('submissionId', 'submissionTime', 'deviceType', 'categoryType','detail_url')


class SubmissionSelectionControlSerializers(serializers.ModelSerializer):
    is_selected = serializers.SerializerMethodField()
    submission = serializers.PrimaryKeyRelatedField(queryset=Submission.objects)
    
    def get_is_selected(self, obj):
        if obj is not None:
            return True
        else: 
            return False
    
    class Meta:
        model = ApprovedSubmission
        fields = ('id', 'is_selected', 'submission',)


class DisplayedSubmissionSerializers(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    def get_author_name(self, obj):
        return obj.submissionUserId.get_full_EN_name()

    class Meta:
        model = Submission
        fields = ('submissionId','deviceType', 'categoryType', 'upload_photo', 'description','author_name')