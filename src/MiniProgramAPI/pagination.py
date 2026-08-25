from urllib.parse import parse_qs, urlparse

from rest_framework.pagination import CursorPagination


class V1CursorPagination(CursorPagination):
    page_size = 20
    page_size_query_param = 'size'
    max_page_size = 50
    cursor_query_param = 'cursor'
    ordering = ('-id',)

    @staticmethod
    def _cursor_from_link(link):
        if not link:
            return None
        return parse_qs(urlparse(link).query).get('cursor', [None])[0]

    def data(self, serialized_items):
        next_cursor = self._cursor_from_link(self.get_next_link())
        return {
            'list': serialized_items,
            'nextCursor': next_cursor,
            'hasMore': next_cursor is not None,
        }
