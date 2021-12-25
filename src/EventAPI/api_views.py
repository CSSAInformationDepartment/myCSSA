from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend

from .paginations import EventsResultsSetPagination
from .filters import EventFilterSet
from .serializers import EventsSerializer
from .models import Event


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = EventsSerializer
    pagination_class = EventsResultsSetPagination 
    filter_backends = [DjangoFilterBackend]
    filterset_class = EventFilterSet
    
    def get_queryset(self):

        if getattr(self, 'swagger_fake_view', False):
            # queryset just for schema generation metadata
            return Event.objects.none()

        return Event.objects \
        .select_related('eventBy', 'eventTypes') \
        .order_by("-eventActualStTime")