from rest_framework.pagination import PageNumberPagination


class MessagePagination(PageNumberPagination):
    """
    PageNumberPagination configured to return 20 messages per page by default.
    Clients can optionally request a custom page size via ?page_size=<n> up to max_page_size.
    """
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100