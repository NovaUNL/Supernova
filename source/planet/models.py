from django.conf import settings
from django.db import models as djm
from django.utils import timezone


class Post(djm.Model):
    name = djm.CharField(max_length=256)
    content = djm.TextField()
    author = djm.ManyToManyField(settings.AUTH_USER_MODEL)
    timestamp = djm.DateTimeField(default=timezone.now)
    # areas = djm.ManyToManyField(Area)

    class Meta:
        unique_together = ['name', 'content']


class Comment(djm.Model):
    post = djm.ForeignKey(Post, on_delete=djm.CASCADE)
    author = djm.ForeignKey(settings.AUTH_USER_MODEL, on_delete=djm.CASCADE, related_name='planet_comments')
    content = djm.TextField()
    timestamp = djm.DateTimeField(default=timezone.now)


VOTE_TYPE_CHOICES = (
    (1, 'upvote'),
    (2, 'downvote'),
    (3, 'award'),
    (4, 'clickbait')
)


# A vote given to a post
class PostVote(djm.Model):
    post = djm.ForeignKey(Post, on_delete=djm.CASCADE)
    type = djm.IntegerField(choices=VOTE_TYPE_CHOICES)
    user = djm.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=djm.SET_NULL)


# A vote given to a comment
class CommentVote(djm.Model):
    comment = djm.ForeignKey(Comment, on_delete=djm.CASCADE)
    type = djm.IntegerField(choices=VOTE_TYPE_CHOICES)
    user = djm.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=djm.SET_NULL)

    class Meta:
        unique_together = ['comment', 'user']
