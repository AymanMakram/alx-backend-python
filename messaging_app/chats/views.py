from django.db.models import Prefetch, Q
from rest_framework import viewsets, status, filters as drf_filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation
from .filters import MessageFilter
from .pagination import MessagePagination


class ConversationViewSet(viewsets.ModelViewSet):
    # ... existing ConversationViewSet unchanged ...
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_fields = ["participants"]
    search_fields = ["participants__username", "participants__email"]
    ordering_fields = ["created_at"]
    ordering = ["created_at"]

    queryset = Conversation.objects.all().prefetch_related(
        Prefetch(
            "messages",
            queryset=Message.objects.select_related("sender").order_by("sent_at"),
            to_attr="ordered_messages_prefetch",
        ),
        "participants",
    )

    def get_queryset(self):
        user = self.request.user
        return self.queryset.filter(participants=user).distinct()

    def perform_create(self, serializer):
        conversation = serializer.save()
        if self.request.user not in conversation.participants.all():
            conversation.participants.add(self.request.user)

    @action(detail=True, methods=["post"], url_path="messages")
    def send_message(self, request, pk=None):
        conversation = self.get_object()
        if request.user not in conversation.participants.all():
            return Response({"detail": "You are not a participant in this conversation."},
                            status=status.HTTP_403_FORBIDDEN)
        data = request.data.copy()
        data["conversation"] = conversation.pk
        serializer = MessageSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        message = serializer.save(sender=request.user)
        return Response(MessageSerializer(message, context={"request": request}).data,
                        status=status.HTTP_201_CREATED)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing and creating Messages.

    - list: lists messages in conversations the authenticated user participates in.
      Supports filtering by conversation via ?conversation=<id> and other filters via MessageFilter.
    - create: send a message by providing 'conversation' (pk) and 'message_body'.
      Sender is taken from request.user automatically.
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = MessageFilter
    pagination_class = MessagePagination
    filterset_fields = ["conversation"]
    search_fields = ["message_body"]
    ordering_fields = ["sent_at"]
    ordering = ["sent_at"]

    queryset = Message.objects.select_related("sender", "conversation").order_by("sent_at")

    def get_queryset(self):
        # Limit messages to those in conversations the user participates in
        user = self.request.user
        qs = self.queryset.filter(conversation__participants=user).distinct()

        # Optional filtering by conversation id (still supported via filter_backends)
        conversation_id = self.request.query_params.get("conversation")
        if conversation_id:
            qs = qs.filter(conversation__pk=conversation_id)
        return qs

    def perform_create(self, serializer):
        convo = None
        conversation_field = serializer.validated_data.get("conversation") or self.request.data.get("conversation")
        if conversation_field:
            convo = get_object_or_404(Conversation, pk=getattr(conversation_field, "pk", conversation_field))
            if self.request.user not in convo.participants.all():
                raise PermissionError("You are not a participant in the target conversation.")
        serializer.save(sender=self.request.user)