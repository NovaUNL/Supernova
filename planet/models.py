from django.contrib.auth.models import User
from django.db import models
from django.db.models import Model, TextField, DateTimeField, ManyToManyField, ForeignKey, IntegerField
from django.utils import timezone

from college.models import Area


class Post(Model):
    name = TextField(max_length=100)
    content = TextField()
    author = ManyToManyField(User)
    timestamp = DateTimeField(default=timezone.now)
    areas = ManyToManyField(Area)

    class Meta:
        unique_together = ['name', 'content']


class Comment(Model):
    post = ForeignKey(Post, on_delete=models.CASCADE)
    author = ForeignKey(User, on_delete=models.CASCADE)
    content = TextField()
    timestamp = DateTimeField(default=timezone.now)


VOTE_TYPE_CHOICES = (
    (1, 'upvote'),
    (2, 'downvote'),
    (3, 'award'),
    (4, 'clickbait')
)


# A vote given to a post
class PostVote(Model):
    post = ForeignKey(Post, on_delete=models.CASCADE)
    type = IntegerField(choices=VOTE_TYPE_CHOICES)
    user = ForeignKey(User, null=True, on_delete=models.SET_NULL)


# A vote given to a comment
class CommentVote(Model):
    comment = ForeignKey(Comment, on_delete=models.CASCADE)
    type = IntegerField(choices=VOTE_TYPE_CHOICES)
    user = ForeignKey(User, null=True, on_delete=models.SET_NULL)

    class Meta:
        unique_together = ['comment', 'user']
