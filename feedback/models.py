from django.db import models
from django.db.models import Model, TextField, ForeignKey, DateTimeField, ManyToManyField, BooleanField
from users.models import User


class Comment(Model):
    author = ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='feedback_comments')
    content = TextField(max_length=1024)
    datetime = DateTimeField(auto_now_add=True)


class Entry(Model):
    title = TextField(max_length=100)
    description = TextField()
    author = ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='feedback_entries')
    comments = ManyToManyField(Comment, through='EntryComment')
    closed = BooleanField()
    reason = TextField(max_length=100)

    class Meta:
        unique_together = ['title', 'author']
        verbose_name_plural = 'entries'


class EntryComment(Model):
    comment = ForeignKey(Comment, on_delete=models.CASCADE)
    entry = ForeignKey(Entry, on_delete=models.CASCADE)
    positive = BooleanField()
