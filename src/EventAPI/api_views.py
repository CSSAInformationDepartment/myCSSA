from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets

from .filters import EventFilterSet
from .models import Event
from .paginations import EventsResultsSetPagination
from .serializers import EventsSerializer


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
