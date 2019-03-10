from django.db import models as djm
from ckeditor_uploader.fields import RichTextUploadingField

from college import models as college
from documents import models as documents
from users import models as users


def area_pic_path(area, filename):
    return f's/a/{area.id}/pic.{filename.split(".")[-1]}'


class Area(djm.Model):
    name = djm.TextField(max_length=50)
    image = djm.ImageField(null=True, upload_to=area_pic_path, verbose_name='imagem')
    img_url = djm.TextField(null=True, blank=True)  # TODO deleteme

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


def subarea_pic_path(subarea, filename):
    return f's/sa/{subarea.id}/pic.{filename.split(".")[-1]}'


class Subarea(djm.Model):
    name = djm.TextField(max_length=50, verbose_name='nome')
    description = djm.TextField(max_length=1024, verbose_name='descrição')
    area = djm.ForeignKey(Area, on_delete=djm.PROTECT, related_name='subareas')
    image = djm.ImageField(null=True, upload_to=subarea_pic_path, verbose_name='imagem')
    img_url = djm.TextField(null=True, blank=True, verbose_name='imagem (url)')  # TODO deleteme

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Topic(djm.Model):
    name = djm.TextField(verbose_name='nome')
    index = djm.IntegerField()
    subarea = djm.ForeignKey(Subarea, on_delete=djm.PROTECT, verbose_name='subarea', related_name='topics')
    sections = djm.ManyToManyField('Section', through='SectionTopic', verbose_name='topics')

    class Meta:
        ordering = ('name',)
        unique_together = ('index', 'subarea')

    def __str__(self):
        return self.name


class Section(djm.Model):
    name = djm.TextField(verbose_name='nome')
    content = RichTextUploadingField(verbose_name='conteúdo', config_name='complex')
    topics = djm.ManyToManyField(Topic, through='SectionTopic', verbose_name='secções')
    requirements = djm.ManyToManyField('Section', verbose_name='requisitos')

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class ClassSection(djm.Model):
    corresponding_class = djm.ForeignKey(college.Class, on_delete=djm.PROTECT)
    section = djm.ForeignKey(Section, on_delete=djm.CASCADE, related_name='class_sections')
    index = djm.IntegerField()

    class Meta:
        unique_together = [('section', 'corresponding_class'), ('index', 'corresponding_class')]

    def __str__(self):
        return f'{self.section} annexed to {self.corresponding_class}.'


class SectionTopic(djm.Model):
    section = djm.ForeignKey(Section, on_delete=djm.CASCADE)
    topic = djm.ForeignKey(Topic, on_delete=djm.PROTECT)
    index = djm.IntegerField()

    class Meta:
        ordering = ('topic', 'index',)
        unique_together = [('section', 'topic'), ('index', 'topic')]

    def __str__(self):
        return f'{self.section} linked to {self.topic} ({self.index}).'


class SectionLog(djm.Model):
    author = djm.ForeignKey(users.User, null=True, blank=True, on_delete=djm.SET_NULL)
    section = djm.ForeignKey(Section, on_delete=djm.CASCADE)
    timestamp = djm.DateTimeField(auto_now_add=True)
    previous_content = djm.TextField(blank=True, null=True)  # TODO Change to diff

    def __str__(self):
        return f'{self.author} edited {self.section} @ {self.timestamp}.'


class SectionSource(djm.Model):
    section = djm.ForeignKey(Section, on_delete=djm.CASCADE, related_name='sources')
    title = djm.TextField(max_length=300, verbose_name='título')
    url = djm.URLField(blank=True, null=True, verbose_name='endreço')

    class Meta:
        unique_together = (('section', 'title'), ('section', 'url'))


class SectionResource(djm.Model):
    section = djm.ForeignKey(Section, on_delete=djm.CASCADE, related_name='resources')
    name = djm.TextField(max_length=100)
    document = djm.ForeignKey(documents.Document, null=True, blank=True, on_delete=djm.PROTECT)
    webpage = djm.URLField(null=True, blank=True)
