from django.db.models import Prefetch
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Conversation, Message, User
from .serializers import ConversationSerializer, MessageSerializer


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing, retrieving and creating Conversations.

    - list: returns conversations the authenticated user participates in.
    - create: create a conversation (participant ids via 'participant_ids' in serializer).
    - retrieve: retrieve a single conversation (includes participants and ordered messages).
    - POST /conversations/{pk}/messages/ : send a message to this conversation.
    """
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    queryset = Conversation.objects.all().prefetch_related(
        Prefetch(
            "messages",
            queryset=Message.objects.select_related("sender").order_by("sent_at"),
            to_attr="ordered_messages_prefetch",
        ),
        "participants",
    )

    def get_queryset(self):
        # Only return conversations the current user participates in
        user = self.request.user
        return self.queryset.filter(participants=user).distinct()

    def perform_create(self, serializer):
        # Create conversation, ensure the requesting user is a participant
        conversation = serializer.save()
        if self.request.user not in conversation.participants.all():
            conversation.participants.add(self.request.user)

    @action(detail=True, methods=["post"], url_path="messages")
    def send_message(self, request, pk=None):
        """
        Send a message to this conversation. The request body should include:
          - message_body (string)

        The conversation id is attached automatically from the URL and the sender is
        set from request.user.
        """
        conversation = self.get_object()

        # Ensure request.user is a participant
        if request.user not in conversation.participants.all():
            return Response({"detail": "You are not a participant in this conversation."},
                            status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        data["conversation"] = conversation.pk  # MessageSerializer expects conversation PK on write

        serializer = MessageSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        message = serializer.save()
        return Response(MessageSerializer(message, context={"request": request}).data,
                        status=status.HTTP_201_CREATED)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing and creating Messages.

    - list: lists messages in conversations the authenticated user participates in.
      Supports filtering by conversation via ?conversation=<id>.
    - create: send a message by providing 'conversation' (pk) and 'message_body'.
      Sender is taken from request.user automatically.
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    queryset = Message.objects.select_related("sender", "conversation").order_by("sent_at")

    def get_queryset(self):
        # Limit messages to those in conversations the user participates in
        user = self.request.user
        qs = self.queryset.filter(conversation__participants=user).distinct()

        # Optional filtering by conversation id
        conversation_id = self.request.query_params.get("conversation")
        if conversation_id:
            qs = qs.filter(conversation__pk=conversation_id)
        return qs

    def perform_create(self, serializer):
        # MessageSerializer.create expects request in context and will set sender from request.user
        serializer.save()