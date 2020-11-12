import reversion
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models as djm
from django.urls import reverse
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify

import settings
from users import models as users


class SuggestionStatus:
    PROPOSED = 0
    PROGRESS = 1
    CLOSED_DONE = 2
    CLOSED_UNDONE = 3
    CHOICES = (
        (PROPOSED, 'proposta'),
        (PROGRESS, 'em progresso'),
        (CLOSED_DONE, 'concluida'),
        (CLOSED_UNDONE, 'rejeitada'))


class Votable(djm.Model):
    votes = GenericRelation('feedback.Vote')
    # Cached
    upvotes = djm.IntegerField(default=0)
    downvotes = djm.IntegerField(default=0)

    class Meta:
        abstract = True

    @property
    def vote_balance(self):
        if self.upvotes is None:
            self.cache_votes()
        return self.upvotes - self.downvotes

    def cache_votes(self):
        self.upvotes = Vote.objects.filter(to=self, type=Vote.UPVOTE).count()
        self.downvotes = Vote.objects.filter(to=self, type=Vote.DOWNVOTE).count()
        self.save()

    def set_vote(self, user, vote_type):
        exists = self.votes.filter(user=user, type=vote_type).exists()
        if exists:
            return

        if vote_type == Vote.UPVOTE:
            deleted_opposite = self.votes.filter(user=user, type=Vote.DOWNVOTE).delete()[0] > 0
            Vote.objects.create(to=self, user=user, type=Vote.UPVOTE)
            self.upvotes += 1
            if deleted_opposite:
                self.downvotes -= 1
            self.save(update_fields=['upvotes', 'downvotes'])
        elif vote_type == Vote.DOWNVOTE:
            deleted_opposite = self.votes.filter(user=user, type=Vote.UPVOTE).delete()[0] > 0
            Vote.objects.create(to=self, user=user, type=Vote.DOWNVOTE)
            self.downvotes += 1
            if deleted_opposite:
                self.upvotes -= 1
            self.save(update_fields=['upvotes', 'downvotes'])
        elif vote_type == Vote.FAVORITE:
            # Delete any existing instances of this vote
            deleted = self.votes.filter(user=user, type=vote_type).delete()
            # None was deleted, this is a set, not an unset
            if not deleted:
                Vote.objects.create(to=self, user=user, type=vote_type)

    def unset_vote(self, user, vote_type):
        deleted = self.votes.filter(user=user, type=vote_type).delete()[0] > 0
        if not deleted:
            return

        if vote_type == Vote.UPVOTE:
            self.upvotes -= 1
            self.save(update_fields=['upvotes'])
        elif vote_type == Vote.DOWNVOTE:
            self.downvotes += 1
            self.save(update_fields=['downvotes'])


class Suggestion(Votable, users.Activity):
    title = djm.CharField(max_length=300)
    content = MarkdownxField(max_length=2000)
    towards_content_type = djm.ForeignKey(ContentType, on_delete=djm.CASCADE, null=True)
    towards_object_id = djm.PositiveIntegerField(null=True)
    towards_object = GenericForeignKey('towards_content_type', 'towards_object_id')
    status = djm.IntegerField(default=SuggestionStatus.PROPOSED, choices=SuggestionStatus.CHOICES)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('feedback:suggestion', args=[self.activity_id])

    def tags(self):
        if self.towards_object_id:
            return [self.towards_object]
        else:
            return []

    @property
    def content_html(self):
        return markdownify(self.content)


class Vote(users.Activity):
    UPVOTE = 0
    DOWNVOTE = 1
    FAVORITE = 2
    VOTE_CHOICES = [
        (UPVOTE, 'positivo'),
        (DOWNVOTE, 'negativo'),
        (FAVORITE, 'favorito'),
    ]
    #: Whether this vote is meant to be anonymous
    anonymity = djm.BooleanField(default=True)
    #: Suggestion to which this vote refers
    content_type = djm.ForeignKey(ContentType, on_delete=djm.CASCADE)
    object_id = djm.PositiveIntegerField()
    to = GenericForeignKey()
    type = djm.IntegerField(choices=VOTE_CHOICES)

    def __str__(self):
        return f'Voto {self.get_type_display()} de {self.user} em "{self.to.title}"'


@reversion.register(follow=['activity_ptr'])
class Review(users.Activity):
    content_type = djm.ForeignKey(ContentType, on_delete=djm.CASCADE)
    object_id = djm.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    text = djm.TextField(null=True, blank=True)
    rating = djm.IntegerField()
    anonymity = djm.BooleanField(default=False)

    def __str__(self):
        return f'Opinião sobre {self.content_object}.'

    def get_absolute_url(self):
        return reverse('feedback:review', args=[self.activity_id])

    @property
    def text_short(self):
        if self.text and len(self.text) > 200:
            return self.text[:200] + " ..."


class Report(djm.Model):
    content_type = djm.ForeignKey(ContentType, on_delete=djm.CASCADE)
    object_id = djm.PositiveIntegerField()
    object = GenericForeignKey('content_type', 'object_id')
    reporter = djm.ForeignKey(settings.AUTH_USER_MODEL, on_delete=djm.CASCADE, related_name='reports')
    information = djm.TextField()

    def __str__(self):
        return f'Denúncia de {self.reporter} a {self.object}'
