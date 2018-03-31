from django.db import models
from django.db.models import Model, TextField, ForeignKey, DateTimeField, DateField, BooleanField, ManyToManyField

from groups.models import Group
from users.models import Profile

KLEEP_TABLE_PREFIX = 'kleep_'


class Conversation(Model):
    creator = ForeignKey(Profile, on_delete=models.PROTECT, related_name='creator')
    date = DateField(auto_now_add=True)
    users = ManyToManyField(Profile, through='ConversationUser')

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'conversations'


class Message(Model):
    author = ForeignKey(Profile, on_delete=models.PROTECT)  # TODO consider user deletion
    datetime = DateTimeField(auto_now_add=True)
    content = TextField()
    conversation = ForeignKey(Conversation, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'messages'


# A user relation to a conversation
class ConversationUser(Model):
    conversation = ForeignKey(Conversation, on_delete=models.CASCADE)
    user = ForeignKey(Profile, on_delete=models.PROTECT)  # TODO consider user deletion
    last_read_message = ForeignKey(Message, null=True, blank=True, on_delete=models.PROTECT)


# A conversation from an outsider to a group
class GroupExternalConversation(Conversation):
    group = ForeignKey(Group, on_delete=models.PROTECT)
    user_ack = BooleanField()
    group_ack = BooleanField()
    closed = BooleanField()

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'group_external_conversations'


# A conversation within a group
class GroupInternalConversation(Conversation):
    group = ForeignKey(Group, on_delete=models.PROTECT)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'group_internal_conversations'
