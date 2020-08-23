from functools import reduce

from django.conf import settings
from django.db import models as djm
from markdownx.utils import markdownify

from college.models import Class
from synopses.models import Section


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
    synopses_sections = djm.ManyToManyField(Section, blank=True, verbose_name='secções de sínteses')

    #: Time this exercise was successfully solved (should be redundant and act as cache)
    successes = djm.IntegerField(default=0)
    #: Number of times users failed to solve this exercise (should be redundant and act as cache)
    failures = djm.IntegerField(default=0)
    #: Number of times users skipped this exercise (should be redundant and act as cache)
    skips = djm.IntegerField(default=0)

    def count_problems(self):
        print(Exercise._count_problems(self.content))
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
            return '<h2>Questão</h2>' \
                   f'<blockquote class="exercise-enunciation">{markdownify(problem["enunciation"])}</blockquote>' \
                   '<ol type="A" class="exercise-answer-candidates">' \
                   f'{"".join(["<li>%s</li>" % markdownify(candidate) for candidate in problem["candidates"]])}' \
                   '</ol>' \
                   '<h2>Resposta</h2>' \
                   '<div class="exercise-answer">' \
                   f"{chr(ord('A') + problem['answerIndex'])}) {markdownify(problem['candidates'][problem['answerIndex']])}" \
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
