from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models
from django.db.models import Model, TextField, ForeignKey, ManyToManyField, IntegerField, DateTimeField, OneToOneField

from college.models import Class
from documents.models import Document
from users.models import User


class Area(Model):
    name = TextField(max_length=50)
    img_url = TextField(null=True, blank=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Subarea(Model):
    name = TextField(max_length=50, verbose_name='nome')
    description = TextField(max_length=1024, verbose_name='descrição')
    area = ForeignKey(Area, on_delete=models.PROTECT, related_name='subareas')
    img_url = TextField(null=True, blank=True, verbose_name='imagem (url)')

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Topic(Model):
    name = TextField(verbose_name='nome')
    index = IntegerField()
    subarea = ForeignKey(Subarea, on_delete=models.PROTECT, verbose_name='subarea', related_name='topics')
    sections = ManyToManyField('Section', through='SectionTopic', verbose_name='topics')

    class Meta:
        ordering = ('name',)
        unique_together = ('index', 'subarea',)

    def __str__(self):
        return self.name


class Section(Model):
    name = TextField(verbose_name='nome')
    content = RichTextUploadingField(verbose_name='conteúdo')
    # example = RichTextField(verbose_name='exemplo') TODO separate
    topics = ManyToManyField(Topic, through='SectionTopic', verbose_name='sections')

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class ClassSection(Model):
    corresponding_class = ForeignKey(Class, on_delete=models.PROTECT)
    section = ForeignKey(Section, on_delete=models.CASCADE, related_name='class_sections')
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
        ordering = ('topic', 'index',)
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

# TODO
# class SectionSource(Model):
#     section = ForeignKey(Section, on_delete=models.CASCADE)
#     title = TextField(max_length=300)
#     url = TextField(max_length=200)


# class SectionRequirement(Model):
#     section = ForeignKey(Section, on_delete=models.CASCADE)
#     requirement = ForeignKey(Section, on_delete=models.CASCADE)


# class SectionContinuation(Model):
#     section = ForeignKey(Section, on_delete=models.CASCADE)
#     continuation = ForeignKey(Section, on_delete=models.CASCADE)

# class Resource(Model):
#     name = TextField(max_length=100)
#     document = OneToOneField(Document, null=True, blank=True, on_delete=models.PROTECT)
#     webpage = TextField(max_length=200)
