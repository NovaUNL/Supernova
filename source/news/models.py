from bs4 import BeautifulSoup
from django.conf import settings
from django.db import models as djm
from django.urls import reverse
from imagekit.models import ImageSpecField
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from pilkit.processors import SmartResize


class NewsTag(djm.Model):
    name = djm.CharField(max_length=32)


def news_item_picture(news_item, filename):
    return f'news/{news_item.id}/pic.{filename.split(".")[-1].lower()}'


class NewsItem(djm.Model):
    title = djm.CharField(max_length=256)
    summary = djm.TextField(max_length=300)
    content = MarkdownxField()
    datetime = djm.DateTimeField()
    edited = djm.BooleanField(default=False)
    edit_note = djm.CharField(null=True, blank=True, default=None, max_length=256)
    edit_datetime = djm.DateTimeField(null=True, blank=True, default=None)
    author = djm.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=djm.SET_NULL,
        related_name='authored_news_items')
    edit_author = djm.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=djm.SET_NULL,
        related_name='edited_news_items')
    tags = djm.ManyToManyField(NewsTag, blank=True)
    source = djm.URLField(null=True, blank=True, max_length=256)
    cover_img = djm.ImageField(null=True, blank=True, max_length=256, upload_to=news_item_picture)
    cover_thumbnail = ImageSpecField(
        source='cover_img',
        processors=[SmartResize(*settings.MEDIUM_ICON_SIZE)],
        format='JPEG',
        options={'quality': settings.MEDIUM_QUALITY})
    generated = djm.BooleanField(default=True)

    class Meta:
        unique_together = ['title', 'datetime']
        ordering = ['datetime', 'title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('news:item', args=[self.id])

    @property
    def content_html(self):
        return markdownify(self.content)

    def gen_summary(self):
        html = markdownify(self.content)
        soup = BeautifulSoup(html, 'html.parser')
        content = soup.text[:300]
        if len(content) < 300:
            summary = content
        else:
            summary = content.rsplit(' ', 1)[0] + " ..."
        if summary != self.summary:
            self.summary = summary


class NewsVote(djm.Model):
    UPVOTE = 1
    DOWNVOTE = 2
    AWARD = 3
    CLICKBAIT = 4

    VOTE_TYPE_CHOICES = (
        (UPVOTE, 'upvote'),
        (DOWNVOTE, 'downvote'),
        (AWARD, 'award'),
        (CLICKBAIT, 'clickbait')
    )
    news_item = djm.ForeignKey(NewsItem, on_delete=djm.CASCADE)
    user = djm.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=djm.SET_NULL)
    vote_type = djm.IntegerField(choices=VOTE_TYPE_CHOICES)


class PinnedNewsItem(djm.Model):
    title = djm.CharField(max_length=256)
    content = MarkdownxField()
    datetime = djm.DateTimeField()
    author = djm.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=djm.SET_NULL,
        related_name='authored_pinned_item')
    edit_datetime = djm.DateTimeField(null=True, blank=True, default=None)
    edit_author = djm.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=djm.SET_NULL,
        related_name='edited_pinned_item')
    active = djm.BooleanField(default=True)

    def __str__(self):
        return f"{self.title}{'' if self.active else ' (inactive)'}"

    def get_absolute_url(self):
        return reverse('news:pinned_item', args=[self.id])

    @property
    def content_html(self):
        return markdownify(self.content)
