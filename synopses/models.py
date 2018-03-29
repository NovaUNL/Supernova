from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Model, TextField, ForeignKey, ManyToManyField, IntegerField, DateTimeField

from kleep.models import KLEEP_TABLE_PREFIX, Class


class SynopsisArea(Model):
    name = TextField(max_length=50)
    img_url = TextField(null=True, blank=True)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'synopsis_area'
        ordering = ('name',)

    def __str__(self):
        return self.name


class SynopsisSubarea(Model):
    name = TextField(max_length=50)
    description = TextField(max_length=1024)
    area = ForeignKey(SynopsisArea, on_delete=models.PROTECT)
    img_url = TextField(null=True, blank=True)

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'synopsis_subarea'
        ordering = ('name',)

    def __str__(self):
        return self.name


class SynopsisTopic(Model):
    name = TextField()
    index = IntegerField()
    sub_area = ForeignKey(SynopsisSubarea, on_delete=models.PROTECT)
    sections = ManyToManyField('SynopsisSection', through='SynopsisSectionTopic')

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'synopsis_topics'
        ordering = ('name',)
        unique_together = ('index', 'sub_area',)

    def __str__(self):
        return self.name


class SynopsisSection(Model):
    name = TextField()
    content = RichTextField()
    topics = ManyToManyField(SynopsisTopic, through='SynopsisSectionTopic')

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'synopsis_sections'
        ordering = ('name',)

    def __str__(self):
        return self.name


class ClassSynopsesSections(Model):
    corresponding_class = ForeignKey(Class, on_delete=models.PROTECT)
    section = ForeignKey(SynopsisSection, on_delete=models.CASCADE)
    index = IntegerField()

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'class_synopsis_sections'
        unique_together = ('section', 'index',)

    def __str__(self):
        return f'{self.section} annexed to {self.corresponding_class.abbreviation}.'


class SynopsisSectionTopic(Model):
    section = ForeignKey(SynopsisSection, on_delete=models.CASCADE)
    topic = ForeignKey(SynopsisTopic, on_delete=models.PROTECT)
    index = IntegerField()

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'synopsis_section_topics'
        ordering = ('section', 'topic', 'index',)
        unique_together = ('section', 'index',)

    def __str__(self):
        return f'{self.section} linked to {self.topic} ({self.index}).'


class SynopsisSectionLog(Model):
    author = ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    section = ForeignKey(SynopsisSection, on_delete=models.CASCADE)
    timestamp = DateTimeField(auto_now_add=True)
    previous_content = TextField(blank=True, null=True)  # TODO Change to diff

    class Meta:
        managed = True
        db_table = KLEEP_TABLE_PREFIX + 'synopsis_section_log'

    def __str__(self):
        return f'{self.author} edited {self.section} @ {self.timestamp}.'
