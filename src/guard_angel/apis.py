import datetime

from django.http import HttpRequest
from django.utils import timezone

from .models import HttpAccessLogModel


def get_request_IPv4(request: HttpRequest) -> str:
    return request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')


def get_previous_path_ip_count_by_hour(request: HttpRequest, path: str, query_string: str = None, hours: int = 24, method='GET') -> int:
    '''
    Returns a value that represents the count of requests from a IP address to a given path in given range of hours.

    The default value of hours is 24, which will look for all requests in 24 hours.

    Optional, query_string can be given to narrow down the counting range

    '''
    count: int = 0
    dt_from: datetime.datetime = timezone.now() - datetime.timedelta(hours=hours)
    IPv4 = get_request_IPv4(request)

    records = HttpAccessLogModel.objects.filter(visitor_ipv4=IPv4
                                                ).filter(time_stamp__gte=dt_from
                                                         ).filter(request_path=path
                                                                  ).filter(request_method=method
                                                                           ).filter(status_code='200')

    if query_string:
        records.filter(request_query_string=query_string)

    count = records.count()

    return count
