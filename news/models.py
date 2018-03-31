from django.db import models
from django.db.models import Model, TextField, DateTimeField, BooleanField, ForeignKey, ManyToManyField, IntegerField

from users.models import User


class NewsTag(Model):
    name = TextField()


class NewsItem(Model):
    title = TextField(max_length=100)
    summary = TextField(max_length=300)
    content = TextField()
    datetime = DateTimeField(auto_now_add=True)
    edited = BooleanField(default=False)
    edit_note = TextField(null=True, blank=True, default=None)
    edit_datetime = DateTimeField(null=True, blank=True, default=None)
    author = ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='author')
    edit_author = ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='edit_author')
    tags = ManyToManyField(NewsTag)

    def __str__(self):
        return self.title


VOTE_TYPE_CHOICES = (
    (1, 'upvote'),
    (2, 'downvote'),
    (3, 'award'),
    (4, 'clickbait')
)


class NewsVote(Model):
    news_item = ForeignKey(NewsItem, on_delete=models.CASCADE)
    user = ForeignKey(User, null=True, on_delete=models.SET_NULL)
    vote_type = IntegerField(choices=VOTE_TYPE_CHOICES)
