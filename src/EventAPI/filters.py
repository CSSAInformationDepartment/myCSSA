from django_filters import rest_framework as filters
from django_filters import DateFilter

from .models import Event

class EventFilterSet(filters.FilterSet):
    """
    Filter events by date range
    """

    start_date_before = DateFilter('eventActualStTime', 'date__lte')
    start_date_after = DateFilter('eventActualStTime', 'date__gte')