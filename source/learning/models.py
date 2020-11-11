from itertools import chain

import reversion
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db.models import Max
from django.urls import reverse
from django.db import models as djm
from imagekit.models import ImageSpecField
from pilkit.processors import SmartResize
from polymorphic.models import PolymorphicModel

from functools import reduce
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from ckeditor_uploader.fields import RichTextUploadingField

from users import models as users
from college import models as college
from documents import models as documents
from feedback import models as feedback
from users.models import Notification


def area_pic_path(area, filename):
    return f's/a/{area.id}/pic.{filename.split(".")[-1].lower()}'


@reversion.register()
class Area(djm.Model):
    """
    A field of knowledge
    """
    #: The title of the area
    title = djm.CharField(max_length=64)
    #: An image that illustrates the area
    image = djm.ImageField(null=True, blank=True, upload_to=area_pic_path)
    image_thumbnail = ImageSpecField(
        source='image',
        processors=[SmartResize(*settings.THUMBNAIL_SIZE)],
        format='JPEG',
        options={'quality': 80})
    image_cover = ImageSpecField(
        source='image',
        processors=[SmartResize(*settings.COVER_SIZE)],
        format='JPEG',
        options={'quality': 80})
    img_url = djm.TextField(null=True, blank=True)  # TODO deleteme

    class Meta:
        ordering = ('title',)

    def __str__(self):
        return self.title


def subarea_pic_path(subarea, filename):
    return f's/sa/{subarea.id}/pic.{filename.split(".")[-1].lower()}'


@reversion.register()
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
    image = djm.ImageField(null=True, blank=True, upload_to=subarea_pic_path, verbose_name='imagem')
    image_thumbnail = ImageSpecField(
        source='image',
        processors=[SmartResize(*settings.THUMBNAIL_SIZE)],
        format='JPEG',
        options={'quality': 80})
    image_cover = ImageSpecField(
        source='image',
        processors=[SmartResize(*settings.COVER_SIZE)],
        format='JPEG',
        options={'quality': 80})
    img_url = djm.TextField(null=True, blank=True, verbose_name='imagem (url)')  # TODO deleteme

    class Meta:
        ordering = ('title',)

    def __str__(self):
        return self.title


@reversion.register()
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
    classes = djm.ManyToManyField(
        college.Class,
        blank=True,
        through='ClassSection',
        related_name='synopsis_sections')
    #: Whether this section has been validated as correct by a teacher
    validated = djm.BooleanField(default=False)

    #: Section type
    TOPIC = 0
    PERSONALITY = 1
    APPLICATION = 2
    type = djm.IntegerField(
        choices=(
            (TOPIC, 'Tópico'),
            (PERSONALITY, 'Personalidade'),
            (APPLICATION, 'Aplicação'),
        ),
        default=TOPIC,
        verbose_name='tipo')

    class Meta:
        ordering = ('title',)

    def __str__(self):
        return f"({self.id}) {self.title}"

    def get_absolute_url(self):
        return reverse('learning:section', args=[self.id])

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
        if self.content_md is not None and len(self.content_md) < 10:
            self.content_md = None
        if self.content_ck is not None and len(self.content_ck) < 10:
            self.content_ck = None

    def most_recent_edit(self, editor):
        return SectionLog.objects.get(section=self, author=editor).order_by('timestamp')

    def compact_indexes(self):
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
    corresponding_class = djm.ForeignKey(college.Class, on_delete=djm.PROTECT, related_name='synopsis_sections_rel')
    section = djm.ForeignKey(Section, on_delete=djm.CASCADE, related_name='classes_rel')
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
            biggest_index = SectionSubsection.objects.filter(parent=self.parent).aggregate(Max('index'))['index__max']
            self.index = 0 if biggest_index is None else biggest_index + 1
        djm.Model.save(self)


class SectionLog(djm.Model):
    """
    The changelog for a section
    """
    author = djm.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=djm.SET_NULL,
                            related_name='_section_logs')
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
    document = djm.ForeignKey(documents.Document, on_delete=djm.PROTECT, related_name='section_resources')

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


@reversion.register()
class Exercise(djm.Model):
    """
    An exercise anyone can try to solve
    """
    #: | Holds three types of objects.
    #: | - Question-answer pairs
    #: `{type:write, enunciation: "...", answer:"..."}`
    #: | - Multiple question
    #: `{type:select, enunciation: "...", candidates:["...", ...], answerIndex:x}`
    #: | - Multiple subproblems (recursive)
    #: - `{type:group, enunciation: "...", subproblems: [object, ...]}`
    content = djm.JSONField()

    #: The :py:class:`users.models.User` which uploaded this exercise
    author = djm.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=djm.SET_NULL,
        related_name='contributed_exercises')
    #: Creation datetime
    datetime = djm.DateTimeField(auto_now_add=True)
    #: Origin of this exercise
    source = djm.CharField(null=True, blank=True, max_length=256, verbose_name='origem')
    #: Optional URL of the origin
    source_url = djm.URLField(null=True, blank=True, verbose_name='endreço')
    #: :py:class:`synopses.models.Section` for which this exercise makes sense (m2m)
    synopses_sections = djm.ManyToManyField(
        Section,
        blank=True,
        verbose_name='secções de sínteses',
        related_name='exercises')

    #: Time this exercise was successfully solved (should be redundant and act as cache)
    successes = djm.IntegerField(default=0)
    #: Number of times users failed to solve this exercise (should be redundant and act as cache)
    failures = djm.IntegerField(default=0)
    #: Number of times users skipped this exercise (should be redundant and act as cache)
    skips = djm.IntegerField(default=0)

    def __str__(self):
        return f'Exercício #{self.id}'

    def count_problems(self):
        return Exercise._count_problems(self.content)

    @staticmethod
    def _count_problems(exercise):
        if exercise['type'] == "group":
            return reduce(lambda x, y: x + y, map(Exercise._count_problems, exercise['subproblems']))
        return 1

    @property
    def render_html(self):
        return self.__render_html_aux(self.content)

    @staticmethod
    def __render_html_aux(problem):
        if (type := problem['type']) == 'group':
            subproblems = "".join(
                [f"<div>{Exercise.__render_html_aux(subproblem)}</div><hr>"
                 for subproblem in problem['subproblems']])
            return '<h2>Grupo</h2>' \
                   f'<blockquote class="exercise-enunciation">{markdownify(problem["enunciation"])}</blockquote>' \
                   f'<div class="subexercises">{subproblems[:-4]}</div>'  # [:-4] ignores last <hr>
        elif type == 'write':
            return '<h2>Questão</h2>' \
                   f'<blockquote class="exercise-enunciation">{markdownify(problem["enunciation"])}</blockquote>' \
                   '<h2>Resposta</h2>' \
                   f'<div class="exercise-answer">{markdownify(problem["answer"])}</div>'
        elif type == 'select':
            # TODO this shouldn't be here, calculate upon upload instead of per request
            answer_count = len(problem["candidates"])
            correct_answer_count = len(problem["answerIndexes"])
            line_num_is_answer = False
            if all(map(
                    lambda c: chr(c[0]) == c[1] or chr(ord('A') + c[0]) == c[1] or chr(ord('a') + c[0]) == c[1],
                    enumerate(problem['candidates']))):
                line_num_is_answer = True
            if line_num_is_answer:
                answers = ""
                correct_answers = "".join(
                    [f"{problem['candidates'][index]}, "
                     for index in problem['answerIndexes']])[:-2]
            else:
                answers = "".join(["<li>%s</li>" % markdownify(candidate) for candidate in problem["candidates"]])
                correct_answers = "".join(
                    [f"{chr(ord('A') + index)}) {markdownify(problem['candidates'][index])}"
                     for index in problem['answerIndexes']])
            return '<h2>Questão</h2>' \
                   f'<blockquote class="exercise-enunciation">{markdownify(problem["enunciation"])}</blockquote>' \
                   f'<ol type="A" class="exercise-answer-candidates">{answers}</ol>' \
                   f'<h2>Resposta{"s" if correct_answer_count > 1 else ""}</h2>' \
                   '<div class="exercise-answer">' \
                   f'{correct_answers}' \
                   '</div>'
        else:
            raise Exception("Attempted to render an exercise which is not fully implemented")


class UserExerciseLog:
    """
    Relation between :py:class:`users.models.User` and :py:class:`Exercise` which represents an attempt.
    """
    OPENED = 0  #: User opened the exercise
    SKIPPED = 1  #: User skipped the exercise
    WRONG = 2  #: User gave a wrong answer to the exercise
    DONE = 3  #: User solved the exercise

    CONCLUSION_CHOICES = (
        (OPENED, 'opened'),
        (SKIPPED, 'skipped'),
        (WRONG, 'wrong'),
        (DONE, 'done')
    )

    #: :py:class:`users.models.User` which attempted to solve this exercise
    user = djm.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=djm.SET_NULL, related_name='exercises')
    #: :py:class:`users.models.Exercise` being attempted
    exercise = djm.ForeignKey(Exercise, on_delete=djm.CASCADE, related_name='users')
    #: Attempt result
    status = djm.IntegerField(choices=CONCLUSION_CHOICES)
    #: (Optional) Given answer
    given_answer = djm.JSONField(null=True, blank=True)
    #: Attempt datetime
    datetime = djm.DateTimeField(auto_now=True)


class WrongAnswerReport:
    """
    An user submitted report of an exercise which has a wrong answer.
    """
    #: :py:class:`users.models.User` reporter
    user = djm.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=djm.SET_NULL,
        related_name='wrong_answer_reports')
    #: :py:class:`Exercise` being reported
    exercise = djm.ForeignKey(Exercise, on_delete=djm.CASCADE, related_name='wrong_answer_reports')
    #: The issue
    reason = djm.TextField()


class Postable(feedback.Votable, djm.Model):
    #: Posted content
    content = MarkdownxField()
    #: Creation datetime
    creation_timestamp = djm.DateTimeField(auto_now_add=True)
    #: Edit datetime
    edit_timestamp = djm.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    @property
    def content_html(self):
        return markdownify(self.content)


@reversion.register(follow=['activity_ptr'])
class Question(users.Activity, Postable):
    """
    A generic question, usually about an exercise.
    """
    #: A descriptive title
    title = djm.CharField(max_length=128)
    #: The related :py:class:`synopses.models.Section`
    linked_sections = djm.ManyToManyField(
        Section,
        blank=True,
        verbose_name='Secções relacionadas',
        related_name='linked_questions')
    #: The related :py:class:`exercises.models.Exercise`
    linked_exercises = djm.ManyToManyField(
        Exercise,
        blank=True,
        verbose_name='Exercícios relacionados',
        related_name='linked_questions')
    #: The related :py:class:`college.models.Class`
    linked_classes = djm.ManyToManyField(
        college.Class,
        blank=True,
        verbose_name='Unidades curriculares relacionadas',
        related_name='linked_questions')
    #: Question that makes this one redundant
    duplication_of = djm.ForeignKey(
        'self',
        blank=True,
        null=True,
        on_delete=djm.SET_NULL,
        related_name='duplicates')
    #: :py:class:`Answer` which answers this question
    decided_answer = djm.OneToOneField(
        'Answer',
        null=True,
        blank=True,
        on_delete=djm.PROTECT,
        related_name='answered_question')
    #: :py:class:`Answer` which teachers decided on
    teacher_decided_answer = djm.OneToOneField(
        'Answer',
        null=True,
        blank=True,
        on_delete=djm.PROTECT,
        related_name='answered_question_teacher')
    #: The teacher that accepted the teacher chosen answer
    deciding_teacher = djm.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=djm.SET_NULL,
        related_name='answered_questions_teacher')

    votes = GenericRelation('feedback.Vote', related_query_name='question')

    def __str__(self):
        return f"questão '{self.title}'"

    def tags(self):
        return chain(self.linked_classes.all(), self.linked_sections.all())

    def get_absolute_url(self):
        return reverse('learning:question', args=[self.activity_id])

    @property
    def answered(self):
        return self.decided_answer is not None

    @property
    def teacher_answered(self):
        return self.teacher_decided_answer is not None


@reversion.register(follow=['activity_ptr'])
class Answer(users.Activity, Postable):
    """
    An answer to a Question
    """
    #: :py:class:`Question` to which this answer refers
    to = djm.ForeignKey(Question, on_delete=djm.PROTECT, related_name='answers')

    votes = GenericRelation('feedback.Vote', related_query_name='answer')

    def __str__(self):
        return f"Resposta a {self.to}."

    def get_absolute_url(self):
        # TODO insert anchors in the template, point to the correct anchor
        return reverse('learning:question', args=[self.to.activity_id])


class AnswerNotification(Notification):
    """A notification about a new answer"""
    #: The answer associated with this notification
    answer = djm.ForeignKey(Answer, on_delete=djm.CASCADE)

    def to_api(self):
        result = super(AnswerNotification, self).to_api()
        result['message'] = f'Nova resposta a "{self.answer.to.title}"'
        result['url'] = self.answer.get_absolute_url()
        result['type'] = 'Resposta'
        return result

    def to_url(self):
        return self.answer.get_absolute_url()

    def __str__(self):
        return f'Nova resposta em: {self.answer.question.title}'
