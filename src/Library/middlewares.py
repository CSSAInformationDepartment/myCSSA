from django.db import connection
from logging import getLogger

logger = getLogger(__name__)

# from https://www.dabapps.com/blog/logging-sql-queries-django-13/
def QueryCountDebugMiddleware(get_response):
    """
    This middleware will log the number of queries run
    and the total time taken for each request. It does not currently support
    multi-db setups.
    """

    def process_response(request):
        total_time = 0

        response = get_response(request)

        for query in connection.queries:
            query_time = query.get('time')
            if query_time is None:
                # django-debug-toolbar monkeypatches the connection
                # cursor wrapper and adds extra information in each
                # item in connection.queries. The query time is stored
                # under the key "duration" rather than "time" and is
                # in milliseconds, not seconds.
                query_time = query.get('duration', 0) / 1000
            total_time += float(query_time)

        logger.warning('%s queries run, total %s seconds' % (len(connection.queries), total_time))
        return response

    return process_response