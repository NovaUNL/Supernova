from django.conf import settings
from django.db import models as djm
from ckeditor_uploader.fields import RichTextUploadingField

from college import models as college
from documents import models as documents


def area_pic_path(area, filename):
    return f's/a/{area.id}/pic.{filename.split(".")[-1].lower()}'


class Area(djm.Model):
    name = djm.CharField(max_length=64)
    image = djm.ImageField(null=True, upload_to=area_pic_path, verbose_name='imagem')
    img_url = djm.TextField(null=True, blank=True)  # TODO deleteme

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


def subarea_pic_path(subarea, filename):
    return f's/sa/{subarea.id}/pic.{filename.split(".")[-1].lower()}'


class Subarea(djm.Model):
    name = djm.CharField(max_length=128, verbose_name='nome')
    description = djm.TextField(max_length=1024, verbose_name='descrição')
    area = djm.ForeignKey(Area, on_delete=djm.PROTECT, related_name='subareas')
    image = djm.ImageField(null=True, upload_to=subarea_pic_path, verbose_name='imagem')
    img_url = djm.TextField(null=True, blank=True, verbose_name='imagem (url)')  # TODO deleteme

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Section(djm.Model):
    """
    A synopsis section, belonging either directly or indirectly to some topic.
    """
    #: The title of the section
    name = djm.CharField(verbose_name='nome', max_length=128)
    #: The CKEditor-written content (legacy format)
    content = RichTextUploadingField(null=True, blank=True, verbose_name='conteúdo', config_name='complex')
    #: Subareas where this section directly fits in
    subarea = djm.ForeignKey(
        Subarea,
        null=True,
        blank=True,
        on_delete=djm.PROTECT,
        verbose_name='subarea',
        related_name='sections')
    #: Sections that have this section as a subsection
    parents = djm.ManyToManyField(
        'self',
        through='SectionSubsection',
        symmetrical=False,
        blank=True,
        related_name='children',
        verbose_name='parents')
    #: Sections that reference this section as a requirement (dependants)
    requirements = djm.ManyToManyField(
        'self',
        blank=True,
        related_name='required_by',
        verbose_name='requisitos',
        symmetrical=False)
    #: Whether this section has been validated as correct by a teacher
    validated = djm.BooleanField(default=False)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return f"({self.id}) {self.name}"

    def content_reduce(self):
        """
        Detects the absence of content and nullifies the field in that case.
        """
        # TODO, do this properly
        if self.content is not None and len(self.content) < 10:
            self.content = None

    def most_recent_edit(self, editor):
        return SectionLog.objects.get(section=self, author=editor).order_by('timestamp')


class ClassSection(djm.Model):
    corresponding_class = djm.ForeignKey(college.Class, on_delete=djm.PROTECT, related_name='synopsis_sections')
    section = djm.ForeignKey(Section, on_delete=djm.CASCADE, related_name='class_sections')
    index = djm.IntegerField()

    class Meta:
        unique_together = [('section', 'corresponding_class'), ('index', 'corresponding_class')]

    def __str__(self):
        return f'{self.section} annexed to {self.corresponding_class}.'


class SectionSubsection(djm.Model):
    section = djm.ForeignKey(Section, on_delete=djm.CASCADE, related_name='parents_intermediary')
    parent = djm.ForeignKey(Section, on_delete=djm.CASCADE, related_name='children_intermediary')
    index = djm.IntegerField(null=False)

    class Meta:
        ordering = ('parent', 'index',)
        unique_together = [('section', 'parent'), ('index', 'parent')]

    def __str__(self):
        return f'{self.parent} -({self.index})-> {self.section}.'

    def save(self, **kwargs):
        if self.index is None:
            assigned_indexes = SectionSubsection.objects.filter(parent=self.parent).values('index')
            self.index = len(assigned_indexes)
        djm.Model.save(self)


class SectionLog(djm.Model):
    author = djm.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=djm.SET_NULL)
    section = djm.ForeignKey(Section, on_delete=djm.CASCADE)
    timestamp = djm.DateTimeField(auto_now_add=True)
    previous_content = djm.TextField(blank=True, null=True)  # TODO Change to diff

    def __str__(self):
        return f'{self.author} edited {self.section} @ {self.timestamp}.'


class SectionSource(djm.Model):
    section = djm.ForeignKey(Section, on_delete=djm.CASCADE, related_name='sources')
    title = djm.CharField(max_length=300, verbose_name='título')
    url = djm.URLField(blank=True, null=True, verbose_name='endreço')

    class Meta:
        unique_together = (('section', 'title'), ('section', 'url'))


class SectionResource(djm.Model):
    section = djm.ForeignKey(Section, on_delete=djm.CASCADE, related_name='resources')
    name = djm.CharField(max_length=256)
    document = djm.ForeignKey(documents.Document, null=True, blank=True, on_delete=djm.PROTECT)
    webpage = djm.URLField(null=True, blank=True)
