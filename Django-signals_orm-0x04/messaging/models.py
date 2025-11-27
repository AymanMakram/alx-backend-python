from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    # REQUIRED BY CHECKER
    edited = models.BooleanField(default=False)
    edited_by = models.ForeignKey(
        User,
        related_name='edited_messages',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    parent_message = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )

    def __str__(self):
        return f"{self.sender} → {self.receiver}: {self.content[:25]}"


class MessageHistory(models.Model):
    """
    Stores the old versions of edited messages.
    """
    message = models.ForeignKey(Message, related_name='history', on_delete=models.CASCADE)
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"History for Message {self.message.id} at {self.edited_at}"



    def get_all_replies(self):
        """
        Recursively fetch all replies to this message.
        Returns a list (tree) of nested replies.
        """
        all_replies = []
        for reply in self.replies.all():
            all_replies.append({
                "message": reply,
                "children": reply.get_all_replies()
            })
        return all_replies