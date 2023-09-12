# Create your views here.
from django.shortcuts import get_object_or_404
from rest_framework import generics

import LegacyDataAPI.serializers as ModelSerializers
from LegacyDataAPI import models


class MultipleFieldLookupORMixin(object):
    """
    Actual code http://www.django-rest-framework.org/api-guide/generic-views/#creating-custom-mixins
    Apply this mixin to any view or viewset to get multiple field filtering
    based on a `lookup_fields` attribute, instead of the default single field filtering.
    """

    def get_object(self):
        queryset = self.get_queryset()             # Get the base queryset
        queryset = self.filter_queryset(queryset)  # Apply any filter backends
        filter = {}
        for field in self.lookup_fields:
            try:                                  # Get the result with one or more fields.
                filter[field] = self.kwargs[field]
            except Exception:
                pass
        return get_object_or_404(queryset, **filter)  # Lookup the object


class LegacyUserLookup(MultipleFieldLookupORMixin, generics.RetrieveAPIView):
    queryset = models.LegacyUsers.objects.all()
    serializer_class = ModelSerializers.LegacyUserSerializers
    lookup_fields = ('email')


class LegacyUserCheck(MultipleFieldLookupORMixin, generics.RetrieveAPIView):
    queryset = models.LegacyUsers.objects.all()
    serializer_class = ModelSerializers.LegitCheck
    lookup_fields = ('membershipId', 'studentId', 'firstNameEN',
                     'lastNameEN', 'dateOfBirth', 'telNumber', 'email')


class ExpCreateLegacyUser(generics.ListCreateAPIView):
    queryset = models.LegacyUsers.objects.all()
    serializer_class = ModelSerializers.LegacyUserSerializers
