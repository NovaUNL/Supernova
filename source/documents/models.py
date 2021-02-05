from django.conf import settings
from django.db import models as djm

from college.models import Place, Building
from groups.models import Group


class Document(djm.Model):
    author_user = djm.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=djm.SET_NULL,
        related_name='document_author')
    author_group = djm.ForeignKey(Group, null=True, blank=True, on_delete=djm.SET_NULL)
    title = djm.CharField(max_length=256)
    content = djm.TextField()
    creation = djm.DateField(auto_now_add=True)
    public = djm.BooleanField(default=False)
    last_edition = djm.DateTimeField(null=True, blank=True, default=None)
    last_editor = djm.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        default=None,
        on_delete=djm.SET_NULL,
        related_name='document_editor')

    class Meta:
        ordering = ['creation']

    def __str__(self):
        return f'{self.title}, {self.author_user}'


class UserPermission(djm.Model):
    document = djm.ForeignKey(Document, on_delete=djm.CASCADE)
    user = djm.ForeignKey(settings.AUTH_USER_MODEL, on_delete=djm.CASCADE)


class GroupPermission(djm.Model):
    document = djm.ForeignKey(Document, on_delete=djm.CASCADE)
    group = djm.ForeignKey(Group, on_delete=djm.CASCADE)
