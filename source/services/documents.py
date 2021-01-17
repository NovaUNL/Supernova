from django.conf import settings
from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry
from services import models as m


@registry.register_document
class ServiceDocument(Document):
    class Index:
        name = 'groups'
        settings = settings.ELASTIC_INDEX_SETTINGS

    class Django:
        model = m.Service
        fields = [
            'name',
            # 'description', TODO add
        ]
        ignore_signals = settings.ELASTIC_IGNORE_SIGNALS
        auto_refresh = settings.ELASTIC_AUTO_REFRESH
        queryset_pagination = settings.ELASTIC_QUERYSET_PAGINATION
