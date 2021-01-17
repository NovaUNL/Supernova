from django.conf import settings
from django_elasticsearch_dsl import Document, TextField
from django_elasticsearch_dsl.registries import registry
from news import models as m


@registry.register_document
class NewsItemDocument(Document):
    content = TextField()

    def prepare_content(self, instance):
        # TODO remove markdown
        return str(instance.content)

    class Index:
        name = 'news_items'
        settings = settings.ELASTIC_INDEX_SETTINGS

    class Django:
        model = m.NewsItem
        fields = ['title']
        ignore_signals = settings.ELASTIC_IGNORE_SIGNALS
        auto_refresh = settings.ELASTIC_AUTO_REFRESH
        queryset_pagination = settings.ELASTIC_QUERYSET_PAGINATION
