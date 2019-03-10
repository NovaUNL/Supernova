from django.db import models as djm
from users.models import User


class Comment(djm.Model):
    author = djm.ForeignKey(User, null=True, on_delete=djm.SET_NULL, related_name='feedback_comments')
    content = djm.TextField(max_length=1024)
    datetime = djm.DateTimeField(auto_now_add=True)


class Entry(djm.Model):
    title = djm.CharField(max_length=128)
    description = djm.TextField()
    author = djm.ForeignKey(User, null=True, on_delete=djm.SET_NULL, related_name='feedback_entries')
    comments = djm.ManyToManyField(Comment, through='EntryComment')
    closed = djm.BooleanField()
    reason = djm.TextField(max_length=512)

    class Meta:
        unique_together = ['title', 'author']
        verbose_name_plural = 'entries'


class EntryComment(djm.Model):
    comment = djm.ForeignKey(Comment, on_delete=djm.CASCADE)
    entry = djm.ForeignKey(Entry, on_delete=djm.CASCADE)
    positive = djm.BooleanField()
