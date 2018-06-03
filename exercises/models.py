from ckeditor.fields import RichTextField
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import Model, ForeignKey, DateTimeField, CharField, URLField, IntegerField, TextField, \
    ManyToManyField

from college.models import Class
from synopses.models import Section
from users.models import User


# Base class for an exercise.
# Is it not declared as abstract both to be link-able as a generic exercise and to avoid naming clashes
class AbstractExercise(Model):
    enunciation = RichTextField(verbose_name='enunciação')  # States the main question
    author = ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='contributed_exercises')
    datetime = DateTimeField(auto_now_add=True)
    explanation = RichTextField(verbose_name='justificação')
    source = CharField(max_length=100, null=True, blank=True, verbose_name='origem')
    source_url = URLField(null=True, blank=True, verbose_name='endreço')
    synopses_sections = ManyToManyField(Section, verbose_name='Secções de sínteses')


# A simple QA pair
class Exercise(AbstractExercise):
    answer = RichTextField(verbose_name='solução')


# A question with multiple answers with one being the correct one
class MultipleChoiceExercise(AbstractExercise):
    possible_answers = ArrayField(RichTextField())
    correct_answer = IntegerField(verbose_name='resposta correta')


# A question with multiple subquestions, each with its own answer
class GroupExercise(AbstractExercise):
    question_answer_pairs = ArrayField(RichTextField(), size=2)


# A question with multiple subquestions, each with multiple answers with one being the correct
class MultipleChoiceGroupExercise(AbstractExercise):
    pass


class MultipleChoiceSubExercise(Model):
    question = ForeignKey(MultipleChoiceGroupExercise, on_delete=models.CASCADE, related_name='exercises')
    enunciation = RichTextField()
    possible_answers = ArrayField(RichTextField())
    correct_answer = IntegerField(verbose_name='resposta correta')


class UserExercise:
    OPENED = 0
    SKIPPED = 1
    WRONG = 2
    DONE = 3

    CONCLUSION_CHOICES = (
        (OPENED, 'opened'),
        (SKIPPED, 'skipped'),
        (WRONG, 'wrong'),
        (DONE, 'done')
    )

    user = ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='exercises')
    exercise = ForeignKey(Exercise, on_delete=models.CASCADE, related_name='users')
    status = IntegerField(choices=CONCLUSION_CHOICES)
    datetime = DateTimeField(auto_now=True)
    attempts = IntegerField(default=0)


class WrongAnswerReport:
    user = ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='wrong_answer_reports')
    exercise = ForeignKey(Exercise, on_delete=models.CASCADE, related_name='wrong_answer_reports')
    reason = TextField()
