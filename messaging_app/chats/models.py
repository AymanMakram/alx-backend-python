import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


# ---------------------------
# Custom User Model
# ---------------------------
class User(AbstractUser):
    """
    Custom User model extending AbstractUser
    - UUID primary key
    - Email unique
    - Phone number optional
    - Role: guest, host, admin
    - Fix reverse accessor clash for groups and user_permissions
    """

    # UUID primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Optional phone number
    phone_number = models.CharField(max_length=20, null=True, blank=True)

    ROLE_CHOICES = (
        ('guest', 'Guest'),
        ('host', 'Host'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='guest')

    created_at = models.DateTimeField(auto_now_add=True)

    # Enforce unique email
    email = models.EmailField(unique=True)

    # Fix reverse accessor clashes
    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_set",
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions_set",
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return f"{self.username} ({self.email})"


# ---------------------------
# Conversation Model
# ---------------------------
class Conversation(models.Model):
    """
    Tracks a conversation between multiple users.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participants = models.ManyToManyField(User, related_name="conversations")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.id}"


# ---------------------------
# Message Model
# ---------------------------
class Message(models.Model):
    """
    Stores messages sent by users within a conversation.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_messages"
    )

    message_body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message {self.id} from {self.sender.username}"
