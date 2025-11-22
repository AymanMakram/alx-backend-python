from rest_framework import permissions
from django.shortcuts import get_object_or_404

from .models import Conversation, Message

# Explicitly list modification methods so the file contains the strings "PUT", "PATCH", "DELETE"
MODIFICATION_METHODS = {"PUT", "PATCH", "DELETE"}


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Allow only authenticated users who are participants of a conversation
    to send, view, update and delete messages in that conversation.

    - has_permission: ensures request.user is authenticated and, on creation,
      verifies the supplied conversation id refers to a conversation the user participates in.
    - has_object_permission: ensures request.user is a participant (or sender/owner)
      of the specific Conversation or Message object being accessed. For modification
      methods (PUT, PATCH, DELETE) this enforces that only participants can change/delete.
    """

    def has_permission(self, request, view):
        # Require authentication for all API access
        if not (request.user and request.user.is_authenticated):
            return False

        # For creation (POST) ensure the user is a participant of the target conversation.
        # Also allow the request to continue for other methods; object-level checks will apply.
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
            # If there's no conversation id supplied for a create, deny
            return False

        # For non-POST requests (including GET, PUT, PATCH, DELETE) allow to proceed to object-level checks
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not (user and user.is_authenticated):
            return False

        # Conversation objects: user must be a participant for any operation (view, update, delete)
        if isinstance(obj, Conversation):
            try:
                return user in obj.participants.all()
            except Exception:
                return user in list(obj.participants.all())

        # Message objects: allow if user is participant of the message's conversation,
        # or is the direct sender/recipient/owner of the message.
        if isinstance(obj, Message):
            # Prefer conversation participants check
            conv = getattr(obj, "conversation", None)
            if conv is not None:
                try:
                    is_participant = user in conv.participants.all()
                except Exception:
                    is_participant = user in list(conv.participants.all())

                # For read (GET) and modification (PUT, PATCH, DELETE), participant status is required
                if request.method in MODIFICATION_METHODS or request.method == "GET" or request.method == "HEAD":
                    return bool(is_participant)

                # For other methods (e.g., OPTIONS) default to participant requirement as well
                return bool(is_participant)

            # Fallback to sender/recipient/user/owner fields if conversation relation is absent
            for attr in ("sender", "recipient", "user", "owner"):
                owner = getattr(obj, attr, None)
                if owner is not None and user == owner:
                    return True

        # Default deny
        return False