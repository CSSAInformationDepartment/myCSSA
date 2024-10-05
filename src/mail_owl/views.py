from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from . import models as PostmanModels
from . import serializers as PostmanSerializers

# Create your views here.


class MailDraftViewSet(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    queryset = PostmanModels.MailDraft.objects.all()
    serializer_class = PostmanSerializers.MailDraftSerializers

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class MailQueneViewSet(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated, )
    queryset = PostmanModels.MailQuene.objects.all()
    serializer_class = PostmanSerializers.MailQueneSerializers
