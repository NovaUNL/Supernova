from django.conf import settings
from django_elasticsearch_dsl import Document, TextField
from django_elasticsearch_dsl.registries import registry
from groups import models as m


@registry.register_document
class GroupDocument(Document):
    description = TextField()

    def prepare_description(self, instance):
        # TODO remove markdown
        return str(instance.description)

    class Index:
        name = 'groups'
        settings = settings.ELASTIC_INDEX_SETTINGS

    class Django:
        model = m.Group
        fields = ['abbreviation', 'name']
        ignore_signals = settings.ELASTIC_IGNORE_SIGNALS
        auto_refresh = settings.ELASTIC_AUTO_REFRESH
        queryset_pagination = settings.ELASTIC_QUERYSET_PAGINATION
