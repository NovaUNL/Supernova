from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models as djm
from markdownx.models import MarkdownxField

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
        votes = self.votes.filter(user=user).all()
        has_upvote = False
        has_downvote = False
        # Counted this way since more types of votes might be implemented
        for vote in votes:
            if vote.type == Vote.UPVOTE:
                has_upvote = True
            if vote.type == Vote.DOWNVOTE:
                has_downvote = True

        if vote_type == Vote.UPVOTE or vote_type == Vote.DOWNVOTE:
            upvote = vote_type == Vote.UPVOTE
            if upvote:
                if has_downvote:
                    self.votes.filter(user=user, type=Vote.DOWNVOTE).update(type=Vote.UPVOTE)
                    self.upvotes += 1
                    self.downvotes -= 1
                elif not has_upvote:
                    Vote.objects.create(to=self, user=user, type=Vote.UPVOTE)
                    self.upvotes += 1
            else:
                if has_upvote:
                    self.votes.filter(user=user, type=Vote.UPVOTE).update(type=Vote.DOWNVOTE)
                    self.upvotes -= 1
                    self.downvotes += 1
                elif not has_downvote:
                    Vote.objects.create(to=self, user=user, type=Vote.DOWNVOTE)
                    self.downvotes += 1
            self.save()


class Suggestion(Votable, users.Activity, users.Subscribable):
    title = djm.CharField(max_length=300)
    content = MarkdownxField(max_length=2000)
    towards_content_type = djm.ForeignKey(ContentType, on_delete=djm.CASCADE)
    towards_object_id = djm.PositiveIntegerField()
    towards_object = GenericForeignKey('towards_content_type', 'towards_object_id')
    status = djm.IntegerField(default=SuggestionStatus.PROPOSED, choices=SuggestionStatus.CHOICES)

    def __str__(self):
        return self.title

    def tags(self):
        return [self.towards_object]


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
    to_content_type = djm.ForeignKey(ContentType, on_delete=djm.CASCADE)
    to_object_id = djm.PositiveIntegerField()
    to_object = GenericForeignKey('to_content_type', 'to_object_id')
    #: Suggestion to which this vote refers
    to = djm.ForeignKey(Suggestion, on_delete=djm.CASCADE, related_name='votes')
    type = djm.IntegerField(choices=VOTE_CHOICES)

    def __str__(self):
        return f'Voto {self.get_type_display()} de {self.user} em "{self.to.title}"'


class Review(users.Activity):
    content_type = djm.ForeignKey(ContentType, on_delete=djm.CASCADE)
    object_id = djm.PositiveIntegerField()
    changed_object = GenericForeignKey('content_type', 'object_id')
    text = djm.TextField()
    rating = djm.IntegerField()

    def __str__(self):
        return f'Análise a {self.changed_object}.'


class Report(djm.Model):
    content_type = djm.ForeignKey(ContentType, on_delete=djm.CASCADE)
    object_id = djm.PositiveIntegerField()
    object = GenericForeignKey('content_type', 'object_id')
    reporter = djm.ForeignKey(settings.AUTH_USER_MODEL, on_delete=djm.CASCADE, related_name='reports')
    information = djm.TextField()

    def __str__(self):
        return f'Denúncia de {self.reporter} a {self.object}'
