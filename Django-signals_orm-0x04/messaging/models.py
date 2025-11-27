from django.db import models
from django.contrib.auth.models import User


class Message(models.Model):
    """
    Main message model. Now includes:
    - `edited`: indicates if message was edited
    - `updated_at`: useful for UI display
    """
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    edited = models.BooleanField(default=False)               # <-- REQUIRED FIELD
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)          # helpful for UI

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver} (edited={self.edited})"


class MessageHistory(models.Model):
    """
    Stores the previous versions of a message.
    Each time the user edits a message, the OLD content
    is saved here by a pre_save signal.
    """
    message = models.ForeignKey(Message, related_name='history', on_delete=models.CASCADE)
    old_content = models.TextField()                          # old version
    edited_at = models.DateTimeField(auto_now_add=True)       # timestamp of edit

    def __str__(self):
        return f"History for Message {self.message.id} -- {self.edited_at}"
