from django.db import models as djm
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify


class Changelog(djm.Model):
    title = djm.TextField(max_length=100)
    content = MarkdownxField()
    date = djm.DateField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def content_html(self):
        return markdownify(self.content)


class Catchphrase(djm.Model):
    phrase = djm.TextField(max_length=100)

    def __str__(self):
        return self.phrase
