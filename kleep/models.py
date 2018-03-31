from django.contrib.auth.models import User, Group
from django.db.models import Model, TextField, DateField
from ckeditor.fields import RichTextField

from college.models import Place, TurnInstance, Building
from users.models import Profile

KLEEP_TABLE_PREFIX = 'kleep_'


class ChangeLog(Model):
    title = TextField(max_length=100)
    content = RichTextField()
    date = DateField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'changelogs'

    def __str__(self):
        return self.title


class Catchphrase(Model):
    phrase = TextField(max_length=100)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'catchphrases'

    def __str__(self):
        return self.phrase
