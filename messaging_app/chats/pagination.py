from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class MessagePagination(PageNumberPagination):
    """
    PageNumberPagination configured to return 20 messages per page by default.

    The get_paginated_response includes page.paginator.count (and an alias 'total_messages')
    so callers/tests that look for page.paginator.count in the response will find it.
    """
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        """
        Return a paginated response that explicitly exposes page.paginator.count.
        """
        # include page.paginator.count explicitly in the response
        return Response({
            "count": self.page.paginator.count,
            "total_messages": self.page.paginator.count,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "results": data,
        })