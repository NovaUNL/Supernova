from django.conf import settings
from django.db import models as djm
from groups.models import Group


class Conversation(djm.Model):
    creator = djm.ForeignKey(settings.AUTH_USER_MODEL, on_delete=djm.PROTECT, related_name='creator')
    date = djm.DateField(auto_now_add=True)
    users = djm.ManyToManyField(settings.AUTH_USER_MODEL, through='ConversationUser')


class Message(djm.Model):
    author = djm.ForeignKey(settings.AUTH_USER_MODEL, on_delete=djm.PROTECT)  # TODO consider user deletion
    datetime = djm.DateTimeField(auto_now_add=True)
    content = djm.TextField()
    conversation = djm.ForeignKey(Conversation, on_delete=djm.CASCADE)

    class Meta:
        unique_together = ['author', 'datetime', 'content', 'conversation']


# A user relation to a conversation
class ConversationUser(djm.Model):
    conversation = djm.ForeignKey(Conversation, on_delete=djm.CASCADE)
    user = djm.ForeignKey(settings.AUTH_USER_MODEL, on_delete=djm.PROTECT)  # TODO consider user deletion
    last_read_message = djm.ForeignKey(Message, null=True, blank=True, on_delete=djm.PROTECT)


# A conversation from an outsider to a group
class GroupExternalConversation(Conversation):
    group = djm.ForeignKey(Group, on_delete=djm.PROTECT)
    user_ack = djm.BooleanField()
    group_ack = djm.BooleanField()
    closed = djm.BooleanField()


# A conversation within a group
class GroupInternalConversation(Conversation):
    group = djm.ForeignKey(Group, on_delete=djm.PROTECT)
