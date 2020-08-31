from django.conf import settings
from django.db import models as djm
from ckeditor_uploader.fields import RichTextUploadingField
from django.urls import reverse
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from polymorphic.models import PolymorphicModel

from college import models as college
from documents import models as documents


def area_pic_path(area, filename):
    return f's/a/{area.id}/pic.{filename.split(".")[-1].lower()}'


class Area(djm.Model):
    """
    A field of knowledge
    """
    #: The title of the area
    title = djm.CharField(max_length=64)
    #: An image that illustrates the area
    image = djm.ImageField(null=True, upload_to=area_pic_path)
    img_url = djm.TextField(null=True, blank=True)  # TODO deleteme

    class Meta:
        ordering = ('title',)

    def __str__(self):
        return self.title


def subarea_pic_path(subarea, filename):
    return f's/sa/{subarea.id}/pic.{filename.split(".")[-1].lower()}'


class Subarea(djm.Model):
    """
    A category inside a field of knowledge (area)
    """
    #: This subarea's title
    title = djm.CharField(max_length=256)
    #: An image that illustrates the area
    description = djm.TextField(max_length=1024, verbose_name='descrição')
    #: The :py:class:`synopses.models.Area` that owns this subarea
    area = djm.ForeignKey(Area, on_delete=djm.PROTECT, related_name='subareas')
    #: An image that illustrates the subarea
    image = djm.ImageField(null=True, upload_to=subarea_pic_path, verbose_name='imagem')
    img_url = djm.TextField(null=True, blank=True, verbose_name='imagem (url)')  # TODO deleteme

    class Meta:
        ordering = ('title',)

    def __str__(self):
        return self.title


class Section(djm.Model):
    """
    A synopsis section, belonging either directly or indirectly to some subarea.
    Sections form a knowledge graph.
    """
    #: The title of the section
    title = djm.CharField(max_length=256)
    #: The markdown content
    content_md = MarkdownxField(null=True, blank=True)
    #: The CKEditor-written content (legacy format)
    content_ck = RichTextUploadingField(null=True, blank=True, config_name='complex')
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
        ordering = ('title',)

    def __str__(self):
        return f"({self.id}) {self.title}"

    @property
    def content(self):
        if self.content_md:
            return markdownify(self.content_md)
        return self.content_ck

    def content_reduce(self):
        """
        Detects the absence of content and nullifies the field in that case.
        """
        # TODO, do this properly
        if self.content is not None and len(self.content) < 10:
            self.content = None

    def most_recent_edit(self, editor):
        return SectionLog.objects.get(section=self, author=editor).order_by('timestamp')

    def _compact_indexes(self):
        index = 0
        for rel in self.children_intermediary.order_by('index').all():
            if index != rel.index:
                rel.index = index
                rel.save()
            index += 1


class ClassSection(djm.Model):
    """
    Model which links a section to a College Class
    """
    corresponding_class = djm.ForeignKey(college.Class, on_delete=djm.PROTECT, related_name='synopsis_sections')
    section = djm.ForeignKey(Section, on_delete=djm.CASCADE, related_name='class_sections')
    index = djm.IntegerField()

    class Meta:
        unique_together = [('section', 'corresponding_class'), ('index', 'corresponding_class')]

    def __str__(self):
        return f'{self.section} annexed to {self.corresponding_class}.'


class SectionSubsection(djm.Model):
    """
    Model which links pairs of parent-children sections.
    """
    #: The child :py:class:`synopses.models.Section`
    section = djm.ForeignKey(Section, on_delete=djm.CASCADE, related_name='parents_intermediary')
    #: The parent :py:class:`synopses.models.Section`
    parent = djm.ForeignKey(Section, on_delete=djm.CASCADE, related_name='children_intermediary')
    #: The position where the referenced section is indexed in the parent
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
    """
    The changelog for a section
    """
    author = djm.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=djm.SET_NULL)
    section = djm.ForeignKey(Section, on_delete=djm.CASCADE, related_name='log_entries')
    timestamp = djm.DateTimeField(auto_now_add=True)
    previous_content = djm.TextField(blank=True, null=True)  # TODO Change to diff

    def __str__(self):
        return f'{self.author} edited {self.section} @ {self.timestamp}.'


class SectionSource(djm.Model):
    """
    Sources the content that a :py:class:`synopses.models.Section` presents.
    """
    #: :py:class:`synopses.models.Section` which references this source
    section = djm.ForeignKey(Section, on_delete=djm.CASCADE, related_name='sources')
    #: Verbose title for this resource
    title = djm.CharField(max_length=256, null=True, blank=True)
    #: Location containing the referenced source
    url = djm.URLField(blank=True, null=True, verbose_name='endreço')

    class Meta:
        ordering = ('section', 'title', 'url')
        unique_together = [('section', 'url'), ]


class SectionResource(PolymorphicModel):
    """
    A resource that is referenced by a :py:class:`synopses.models.Section`.
    Resources are aids aimed at easing the learning experience.
    """
    #: :py:class:`synopses.models.Section` which references this resource
    section = djm.ForeignKey(Section, on_delete=djm.CASCADE, related_name='resources')
    #: Verbose title for this resource
    title = djm.CharField(max_length=256, null=True, blank=True)

    @property
    def template_title(self):
        return "Sem título" if self.title is None else self.title

    @property
    def template_url(self):
        return None


class SectionDocumentResource(SectionResource):
    #: Resource :py:class:`documents.models.Document`
    document = djm.ForeignKey(documents.Document, on_delete=djm.PROTECT)

    @property
    def template_title(self):
        return self.document.title if self.title is None else self.title

    @property
    def template_url(self):
        return reverse('college:department', args=[self.document.id])


class SectionWebResource(SectionResource):
    #: Resource location
    url = djm.URLField()

    @property
    def template_title(self):
        return self.url if self.title is None else self.title

    @property
    def template_url(self):
        return self.url
