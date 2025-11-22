from django_filters import rest_framework as filters
from .models import Message


class MessageFilter(filters.FilterSet):
    """
    FilterSet for MessageViewSet to allow:
    - filtering by conversation id
    - filtering by sender id or sender username
    - filtering by recipient id
    - filtering by participant id (any user in the conversation)
    - filtering by sent_at time range via 'start' (>=) and 'end' (<=)
    Example queries:
      /api/messages/?conversation=3
      /api/messages/?sender=5
      /api/messages/?participant=2&start=2025-01-01T00:00:00Z&end=2025-01-31T23:59:59Z
    """
    conversation = filters.NumberFilter(field_name="conversation__id")
    sender = filters.NumberFilter(field_name="sender__id")
    sender_username = filters.CharFilter(field_name="sender__username", lookup_expr="icontains")
    recipient = filters.NumberFilter(field_name="recipient__id")
    participant = filters.NumberFilter(method="filter_by_participant")
    start = filters.DateTimeFilter(field_name="sent_at", lookup_expr="gte")
    end = filters.DateTimeFilter(field_name="sent_at", lookup_expr="lte")

    class Meta:
        model = Message
        fields = ["conversation", "sender", "recipient", "participant", "start", "end", "sender_username"]

    def filter_by_participant(self, queryset, name, value):
        # Return messages whose conversation contains the given participant user id
        return queryset.filter(conversation__participants__id=value)