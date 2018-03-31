from django.contrib.auth.models import User, Group
from django.db.models import Model, TextField, DateField
from ckeditor.fields import RichTextField


class Changelog(Model):
    title = TextField(max_length=100)
    content = RichTextField()
    date = DateField(auto_now_add=True)

    def __str__(self):
        return self.title


class Catchphrase(Model):
    phrase = TextField(max_length=100)

    def __str__(self):
        return self.phrase
