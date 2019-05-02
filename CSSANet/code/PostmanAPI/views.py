from django.shortcuts import render

from rest_framework import viewsets,generics,mixins
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, BasePermission, DjangoModelPermissionsOrAnonReadOnly

from django.utils.html import html_safe

from . import models as PostmanModels
from . import serializers as PostmanSerializers
# Create your views here.

class MailDraftViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    Provide read-only viewset to inspect saved mail drafts
    
    URL Endpoints:
        - List: ./postman/api/draft/
        - Detail: ./postman/api/draft/<id>/

    Author: Le(Josh). Lu
    '''
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    queryset = PostmanModels.MailDraft.objects.all()
    serializer_class = PostmanSerializers.MailDraftSerializers

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class MailQueneViewSet(viewsets.ModelViewSet):
    '''
    Provide read-only viewset to inspect mail quene
    
    URL Endpoints:
        - List: ./postman/api/quene/
        - Detail: ./postman/api/quene/<id>/

    Author: Le(Josh). Lu
    '''
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated, )
    queryset= PostmanModels.MailQuene.objects.all()
    serializer_class = PostmanSerializers.MailQueneSerializers

class CreateMailDraftAPIView(generics.CreateAPIView):
    '''
    Provide read-only viewset to inspect saved mail drafts
    
    URL Endpoints:
        - List: ./postman/api/draft/
        - Detail: ./postman/api/draft/<id>/

    Author: Le(Josh). Lu
    '''
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated, )
    serializer_class = PostmanSerializers.MailDraftSerializers

