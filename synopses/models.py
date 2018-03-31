from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Model, TextField, ForeignKey, ManyToManyField, IntegerField, DateTimeField

from clip.models import Class


class Area(Model):
    name = TextField(max_length=50)
    img_url = TextField(null=True, blank=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Subarea(Model):
    name = TextField(max_length=50)
    description = TextField(max_length=1024)
    area = ForeignKey(Area, on_delete=models.PROTECT)
    img_url = TextField(null=True, blank=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Topic(Model):
    name = TextField()
    index = IntegerField()
    sub_area = ForeignKey(Subarea, on_delete=models.PROTECT)
    sections = ManyToManyField('Section', through='SectionTopic')

    class Meta:
        ordering = ('name',)
        unique_together = ('index', 'sub_area',)

    def __str__(self):
        return self.name


class Section(Model):
    name = TextField()
    content = RichTextField()
    topics = ManyToManyField(Topic, through='SectionTopic')

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class ClassSection(Model):
    corresponding_class = ForeignKey(Class, on_delete=models.PROTECT)
    section = ForeignKey(Section, on_delete=models.CASCADE)
    index = IntegerField()

    class Meta:
        unique_together = ('section', 'index',)

    def __str__(self):
        return f'{self.section} annexed to {self.corresponding_class}.'


class SectionTopic(Model):
    section = ForeignKey(Section, on_delete=models.CASCADE)
    topic = ForeignKey(Topic, on_delete=models.PROTECT)
    index = IntegerField()

    class Meta:
        ordering = ('section', 'topic', 'index',)
        unique_together = ('section', 'index',)

    def __str__(self):
        return f'{self.section} linked to {self.topic} ({self.index}).'


class SectionLog(Model):
    author = ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    section = ForeignKey(Section, on_delete=models.CASCADE)
    timestamp = DateTimeField(auto_now_add=True)
    previous_content = TextField(blank=True, null=True)  # TODO Change to diff

    def __str__(self):
        return f'{self.author} edited {self.section} @ {self.timestamp}.'
