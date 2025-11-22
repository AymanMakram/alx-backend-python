from rest_framework import permissions
from django.shortcuts import get_object_or_404

from .models import Conversation, Message


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Allow only authenticated users who are participants of a conversation
    to send, view, update and delete messages in that conversation.

    - has_permission: ensures request.user is authenticated and, on creation,
      verifies the supplied conversation id refers to a conversation the user participates in.
    - has_object_permission: ensures request.user is a participant (or sender/owner)
      of the specific Conversation or Message object being accessed.
    """

    def has_permission(self, request, view):
        # Require authentication for all API access
        if not (request.user and request.user.is_authenticated):
            return False

        # For creation (POST) ensure the user is a participant of the target conversation.
        # We don't hardcode HTTP verbs to allow view-driven behavior; check for presence
        # of a conversation id where relevant.
        if request.method == "POST":
            conversation_id = (
                request.data.get("conversation")
                or request.query_params.get("conversation")
                or view.kwargs.get("pk")
                or view.kwargs.get("conversation_pk")
            )
            if conversation_id:
                conversation = get_object_or_404(Conversation, pk=conversation_id)
                try:
                    return request.user in conversation.participants.all()
                except Exception:
                    return request.user in list(conversation.participants.all())
            # If there's no conversation id supplied for create, deny
            return False

        # For non-create requests, allow to proceed to object-level permission checks
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not (user and user.is_authenticated):
            return False

        # Conversation objects: user must be a participant
        if isinstance(obj, Conversation):
            try:
                return user in obj.participants.all()
            except Exception:
                return user in list(obj.participants.all())

        # Message objects: allow if user is participant of the message's conversation,
        # or is the direct sender/recipient/owner of the message.
        if isinstance(obj, Message):
            conv = getattr(obj, "conversation", None)
            if conv is not None:
                try:
                    return user in conv.participants.all()
                except Exception:
                    return user in list(conv.participants.all())

            for attr in ("sender", "recipient", "user", "owner"):
                owner = getattr(obj, attr, None)
                if owner is not None and user == owner:
                    return True

        # Default deny
        return False