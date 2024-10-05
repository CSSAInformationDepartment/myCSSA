from rest_framework import serializers

from . import models as PostmanModels


class MailDraftSerializers(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.id')

    class Meta:
        model = PostmanModels.MailDraft
        fields = '__all__'


class MailQueneSerializers(serializers.ModelSerializer):
    class Meta:
        model = PostmanModels.MailQuene
        fields = '__all__'
