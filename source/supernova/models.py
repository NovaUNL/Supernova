from django.db import models as djm
from django.urls import reverse
from django.conf import settings

from markdownx.models import MarkdownxField
from markdownx.utils import markdownify

from users.models import Notification


class Catchphrase(djm.Model):
    """A generic slogan that is shown beneath the title."""
    #: The presented phrase
    phrase = djm.TextField(max_length=100)

    def __str__(self):
        return self.phrase


class Changelog(djm.Model):
    """A verbose list of changes since the past major version"""
    #: The entry title
    title = djm.CharField(max_length=100)
    #: The entry content
    content = MarkdownxField()
    #: Publish date
    date = djm.DateField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def content_html(self):
        return markdownify(self.content)


class ChangelogNotification(Notification):
    """A notification about a new changelog entry"""
    #: The notification associated with a :py:class:`Changelog`
    entry = djm.ForeignKey(Changelog, on_delete=djm.CASCADE)

    def to_api(self):
        result = super(ChangelogNotification, self).to_api()
        result['message'] = f'Nova versão do Supernova: {self.entry.title}'
        result['url'] = reverse('changelog')
        result['type'] = 'Alteração'
        return result

    def to_url(self):
        return reverse('changelog')

    def __str__(self):
        return f'Nova versão do Supernova: {self.entry.title}'


class SupportPledge(djm.Model):
    INDEPENDENT = 0
    INDEPENDENT_SUPPORTED = 1
    ASSOCIATION_COMPLEMENT = 2
    ASSOCIATION_REPLACEMENT = 3
    CHOICES = [
        (INDEPENDENT, 'Independente'),
        (INDEPENDENT_SUPPORTED, 'Independente com suporte'),
        (ASSOCIATION_COMPLEMENT, 'Associado em complemento'),
        (ASSOCIATION_REPLACEMENT, 'Associado para substituição'),
    ]
    user = djm.OneToOneField(settings.AUTH_USER_MODEL, on_delete=djm.CASCADE, related_name='pledge')
    pledge_towards = djm.IntegerField(choices=CHOICES)
    anonymous = djm.BooleanField(default=False)
    comment = djm.TextField(null=True, blank=True)
