from django.db import models
from django.contrib.auth import get_user_model
from .managers import UnreadMessagesManager

User = get_user_model()


class UnreadMessagesManager(models.Manager):
    """Custom manager to return unread messages for a specific user."""
    def for_user(self, user):
        return (
            super()
            .get_queryset()
            .filter(receiver=user, read=False)
            .only("id", "sender", "content", "timestamp")  # Optimized
        )


class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    # Edit tracking
    edited = models.BooleanField(default=False)
    edited_by = models.ForeignKey(User, null=True, blank=True, related_name="edited_messages", on_delete=models.SET_NULL)

    # Threading
    parent_message = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)

    # Read/unread
    read = models.BooleanField(default=False)

    # Managers
    objects = models.Manager()          # Default
    unread = UnreadMessagesManager()    # Custom manager for unread messages

    def __str__(self):
        return f"{self.sender} → {self.receiver}: {self.content[:25]}"

    def get_all_replies(self):
        """
        Recursively fetch all replies in threaded format.
        Returns a list of dicts: {message: Message, children: [nested replies]}
        """
        all_replies = []
        for reply in self.replies.all():
            all_replies.append({
                "message": reply,
                "children": reply.get_all_replies()
            })
        return all_replies


class MessageHistory(models.Model):
    """
    Stores previous versions of messages whenever they are edited.
    """
    message = models.ForeignKey(Message, related_name='history', on_delete=models.CASCADE)
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"History of Message ID {self.message.id} at {self.edited_at}"


class Notification(models.Model):
    """
    Notifications for users when a new message is received.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user} about Message {self.message.id}"
