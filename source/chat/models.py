from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models as djm
from markdownx.models import MarkdownxField
from polymorphic.models import PolymorphicModel

from users import models as users
from groups import models as groups


class Conversation(PolymorphicModel):
    """
    A private conversation
    """
    #: The user which instantiated this conversation
    creator = djm.ForeignKey(settings.AUTH_USER_MODEL, on_delete=djm.PROTECT, related_name='creator')
    #: The datetime when this room was created
    creation = djm.DateTimeField(auto_now_add=True)
    #: Users engaging in this conversation
    users = djm.ManyToManyField(settings.AUTH_USER_MODEL, through='ConversationUser')
    # Cached
    #: Timestamp of the last activity
    last_activity = djm.DateTimeField(null=True)


class Message(djm.Model):
    """
    A message in a conversation
    """
    #: User who authored this message
    author = djm.ForeignKey(settings.AUTH_USER_MODEL, on_delete=djm.PROTECT)
    #: The datetime when this message was sent
    creation = djm.DateTimeField(auto_now_add=True)
    #: This message's textual content
    content = djm.TextField()
    #: Conversation to which this message belongs
    conversation = djm.ForeignKey(Conversation, on_delete=djm.CASCADE, related_name='messages')
    #: Datetime of the last edit
    last_message_edition = djm.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['author', 'creation', 'content', 'conversation']


class ConversationUser(djm.Model):
    """
    The presence of an user in a conversation
    """
    #: Conversation in this relationship
    conversation = djm.ForeignKey(Conversation, on_delete=djm.CASCADE)
    #: User in this relationship
    user = djm.ForeignKey(settings.AUTH_USER_MODEL, on_delete=djm.PROTECT)
    #: The last message this user read
    last_read_message = djm.ForeignKey(Message, null=True, blank=True, on_delete=djm.PROTECT)


class Room(Conversation):
    """
    A thematic chat room
    """
    #: A textual identifier for this room
    identifier = djm.CharField(max_length=32)
    #: The name of this conversation (creator designated textual identifier)
    name = djm.CharField(max_length=300)
    #: A description of what this conversation is about
    description = djm.TextField(null=True, blank=True)
    #: Whether anonymous users are allowed
    anonymous_allowed = djm.BooleanField(default=False)


class GroupExternalConversation(Conversation):
    """
    A conversation between a user the members of a group, meant to be used as a mean to provide support.
    """
    #: Conversation title
    title = djm.CharField(max_length=300)
    #: The group where a conversation happened
    group = djm.ForeignKey(groups.Group, on_delete=djm.PROTECT)
    #: Flag signaling conversation closure
    closed = djm.BooleanField()
    # Cached fields
    #: Whether the user has read the last message
    user_ack = djm.BooleanField()
    #: Whether a group member has read the last message
    group_ack = djm.BooleanField()


class GroupInternalConversation(Conversation):
    """
    A conversation within the members of a group, possibly to discuss topics internally
    """
    #: Conversation title
    title = djm.CharField(max_length=300)
    #: The group where a conversation happened
    group = djm.ForeignKey(groups.Group, on_delete=djm.PROTECT)


class Comment(users.Activity):
    """
    A comment to an arbitrary object
    """
    to_content_type = djm.ForeignKey(ContentType, on_delete=djm.CASCADE)
    to_object_id = djm.PositiveIntegerField()
    #: Object to which this comment refers
    to_object = GenericForeignKey('to_content_type', 'to_object_id')
    #: Posted content
    content = MarkdownxField()
    #: Creation datetime
    creation_timestamp = djm.DateTimeField(auto_now_add=True)
    #: Edit datetime
    edit_timestamp = djm.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comentário em '{self.to_object}'"
