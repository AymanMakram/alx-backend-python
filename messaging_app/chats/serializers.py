from rest_framework import serializers
from .models import User, Conversation, Message


# ---------------------------
# User Serializer
# ---------------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "user_id",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "role",
            "created_at",
        ]


# ---------------------------
# Message Serializer
# ---------------------------
class MessageSerializer(serializers.ModelSerializer):
    # Nested read-only sender info
    sender = UserSerializer(read_only=True)
    # Accept conversation id on write, but don't nest it on read
    conversation = serializers.PrimaryKeyRelatedField(
        queryset=Conversation.objects.all(), write_only=True
    )
    message_body = serializers.CharField()

    class Meta:
        model = Message
        fields = [
            "message_id",
            "conversation",
            "sender",
            "message_body",
            "sent_at",
        ]
        read_only_fields = ("message_id", "sender", "sent_at")

    def create(self, validated_data):
        """
        Set the sender from the request user and attach the conversation.
        """
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user is None or not user.is_authenticated:
            raise serializers.ValidationError("Authentication credentials were not provided.")
        conversation = validated_data.pop("conversation")
        message = Message.objects.create(sender=user, conversation=conversation, **validated_data)
        return message

    def to_representation(self, instance):
        """
        Represent conversation as its id (conversation_id) instead of full nested object.
        Keep sender nested.
        """
        rep = super().to_representation(instance)
        # Replace the write-only conversation field with the conversation id for clarity
        rep["conversation"] = getattr(instance.conversation, "conversation_id", None)
        return rep


# ---------------------------
# Conversation Serializer
# ---------------------------
class ConversationSerializer(serializers.ModelSerializer):
    # Read nested participants
    participants = UserSerializer(many=True, read_only=True)
    # Allow providing participant ids on write
    participant_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, queryset=User.objects.all(), source="participants"
    )

    # Return ordered messages for the conversation (read-only)
    messages = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "conversation_id",
            "participants",     # read-only nested users
            "participant_ids",  # write-only helper for creating/updating
            "messages",         # read-only nested messages ordered by sent_at
            "created_at",
        ]
        read_only_fields = ("conversation_id", "participants", "messages", "created_at")

    def get_messages(self, obj):
        """
        Return messages ordered by sent_at (oldest first).
        """
        qs = obj.messages.order_by("sent_at")
        return MessageSerializer(qs, many=True, context=self.context).data

    def validate(self, attrs):
        """
        Ensure there are at least two participants for a conversation.
        The 'participants' value will be available in attrs due to source="participants"
        when participant_ids are provided on write.
        """
        participants = attrs.get("participants")
        if participants is None:
            # When not provided during update/create, no validation needed here.
            return attrs
        if len(participants) < 2:
            raise serializers.ValidationError("A conversation must have at least two participants.")
        return attrs

    def create(self, validated_data):
        """
        Create a conversation and attach participants.
        """
        participants = validated_data.pop("participants", [])
        conversation = Conversation.objects.create(**validated_data)
        if participants:
            conversation.participants.set(participants)
        return conversation

    def update(self, instance, validated_data):
        """
        Update participants if provided; other fields are read-only presently.
        """
        participants = validated_data.pop("participants", None)
        if participants is not None:
            instance.participants.set(participants)
        instance.save()
        return instance