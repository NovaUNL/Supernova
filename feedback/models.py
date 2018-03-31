from django.db import models
from django.db.models import Model, TextField, ForeignKey, DateTimeField, ManyToManyField, BooleanField
from kleep.models import KLEEP_TABLE_PREFIX
from users.models import Profile


class Comment(Model):
    author = ForeignKey(Profile, null=True, on_delete=models.SET_NULL)
    content = TextField(max_length=1024)
    datetime = DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'comments'


class FeedbackEntry(Model):
    title = TextField(max_length=100)
    description = TextField()
    author = ForeignKey(Profile, null=True, on_delete=models.SET_NULL)
    comments = ManyToManyField(Comment, through='FeedbackEntryComment')
    closed = BooleanField()
    reason = TextField(max_length=100)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'feedback_entries'


class FeedbackEntryComment(Model):
    comment = ForeignKey(Comment, on_delete=models.CASCADE)
    entry = ForeignKey(FeedbackEntry, on_delete=models.CASCADE)
    positive = BooleanField()

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'feedback_entry_comments'
