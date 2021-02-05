from django.conf import settings
from django_elasticsearch_dsl import Document, TextField
from django_elasticsearch_dsl.registries import registry
from learning import models as m


@registry.register_document
class SectionDocument(Document):
    content = TextField()

    def prepare_content(self, instance):
        # TODO remove markdown
        return str(instance.content)

    class Index:
        name = 'sections'
        settings = settings.ELASTIC_INDEX_SETTINGS

    class Django:
        model = m.Section
        fields = ['title']
        ignore_signals = settings.ELASTIC_IGNORE_SIGNALS
        auto_refresh = settings.ELASTIC_AUTO_REFRESH
        queryset_pagination = settings.ELASTIC_QUERYSET_PAGINATION


@registry.register_document
class ExerciseDocument(Document):
    content = TextField()

    def prepare_content(self, instance):
        # TODO remove markdown
        return str(instance.raw_text)

    class Index:
        name = 'exercises'
        settings = settings.ELASTIC_INDEX_SETTINGS

    class Django:
        model = m.Exercise
        ignore_signals = settings.ELASTIC_IGNORE_SIGNALS
        auto_refresh = settings.ELASTIC_AUTO_REFRESH
        queryset_pagination = settings.ELASTIC_QUERYSET_PAGINATION


@registry.register_document
class QuestionDocument(Document):
    content = TextField()
    answers = TextField()

    def prepare_content(self, instance):
        # TODO remove markdown
        return str(instance.content)

    def prepare_answers(self, instance):
        # TODO remove markdown
        return " ".join(instance.answers.values_list('content', flat=True))

    class Index:
        name = 'questions'
        settings = settings.ELASTIC_INDEX_SETTINGS

    class Django:
        model = m.Question
        fields = ['title']
        ignore_signals = settings.ELASTIC_IGNORE_SIGNALS
        auto_refresh = settings.ELASTIC_AUTO_REFRESH
        queryset_pagination = settings.ELASTIC_QUERYSET_PAGINATION