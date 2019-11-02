from django.db import models as djm
from ckeditor.fields import RichTextField


class Changelog(djm.Model):
    title = djm.TextField(max_length=100)
    content = RichTextField()
    date = djm.DateField(auto_now_add=True)

    def __str__(self):
        return self.title


class Catchphrase(djm.Model):
    phrase = djm.TextField(max_length=100)

    def __str__(self):
        return self.phrase
