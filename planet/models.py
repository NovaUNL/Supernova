from django.contrib.auth.models import User
from django.db import models
from django.db.models import Model, TextField, DateTimeField, ManyToManyField, ForeignKey, IntegerField
from django.utils import timezone

from college.models import Area
from kleep.models import KLEEP_TABLE_PREFIX


class Post(Model):
    name = TextField(max_length=100)
    content = TextField()
    author = ManyToManyField(User)
    timestamp = DateTimeField(default=timezone.now)
    areas = ManyToManyField(Area)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'planet_post'


class Comment(Model):
    post = ForeignKey(Post, on_delete=models.CASCADE)
    author = ForeignKey(User, on_delete=models.CASCADE)
    content = TextField()
    timestamp = DateTimeField(default=timezone.now)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'planet_comment'


VOTE_TYPE_CHOICES = (
    (1, 'upvote'),
    (2, 'downvote'),
    (3, 'award'),
    (4, 'clickbait')
)


class PostVote(Model):
    post = ForeignKey(Post, on_delete=models.CASCADE)
    type = IntegerField(choices=VOTE_TYPE_CHOICES)
    user = ForeignKey(User, null=True, on_delete=models.SET_NULL)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'planet_post_votes'


class CommentVote(Model):
    comment = ForeignKey(Comment, on_delete=models.CASCADE)
    type = IntegerField(choices=VOTE_TYPE_CHOICES)
    user = ForeignKey(User, null=True, on_delete=models.SET_NULL)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'planet_comment_votes'
