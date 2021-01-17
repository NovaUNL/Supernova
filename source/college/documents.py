from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry
from college import models as m

# Ignore auto updating of Elasticsearch when a model is saved or deleted:
_ignore_signals = True
# Don't perform an index refresh after every update (overrides global setting):
_auto_refresh = False
# Paginate the django queryset used to populate the index with the specified size
# (by default it uses the database driver's default setting)
_queryset_pagination = 5000
_index_settings = {'number_of_shards': 1,
                   'number_of_replicas': 0}


@registry.register_document
class StudentDocument(Document):
    class Index:
        name = 'students'
        settings = _index_settings

    class Django:
        model = m.Student

        # The fields of the model you want to be indexed in Elasticsearch
        fields = [
            'name',
            'number',
            'abbreviation',
            'year',
            'first_year',
            'last_year',
        ]

        ignore_signals = _ignore_signals
        auto_refresh = _auto_refresh
        queryset_pagination = _queryset_pagination


@registry.register_document
class TeacherDocument(Document):
    class Index:
        name = 'teachers'
        settings = _index_settings

    class Django:
        model = m.Teacher

        fields = [
            'name',
            'abbreviation',
            'first_year',
            'last_year',
        ]

        ignore_signals = _ignore_signals
        auto_refresh = _auto_refresh
        queryset_pagination = _queryset_pagination


@registry.register_document
class BuildingDocument(Document):
    class Index:
        name = 'buildings'
        settings = _index_settings

    class Django:
        model = m.Building

        # The fields of the model you want to be indexed in Elasticsearch
        fields = [
            'name',
            'abbreviation',
        ]

        ignore_signals = _ignore_signals
        auto_refresh = _auto_refresh
        queryset_pagination = _queryset_pagination


@registry.register_document
class DepartmentDocument(Document):

    class Index:
        name = 'departments'
        settings = _index_settings

    class Django:
        model = m.Department

        # The fields of the model you want to be indexed in Elasticsearch
        fields = [
            'name',
            # 'description',
            # 'url',
        ]

        ignore_signals = _ignore_signals
        auto_refresh = _auto_refresh
        queryset_pagination = _queryset_pagination

    # def prepare_description(self, instance):
    #     return instance.description


@registry.register_document
class RoomDocument(Document):
    class Index:
        name = 'rooms'
        settings = _index_settings

    class Django:
        model = m.Room

        # The fields of the model you want to be indexed in Elasticsearch
        fields = [
            'name',
            'floor',
            'description',
            'door_number',
        ]

        ignore_signals = _ignore_signals
        auto_refresh = _auto_refresh
        queryset_pagination = _queryset_pagination


@registry.register_document
class CourseDocument(Document):
    class Index:
        name = 'course'
        settings = _index_settings

    class Django:
        model = m.Course

        # The fields of the model you want to be indexed in Elasticsearch
        fields = [
            'name',
            'abbreviation',
            # 'description',
        ]

        ignore_signals = _ignore_signals
        auto_refresh = _auto_refresh
        queryset_pagination = _queryset_pagination


@registry.register_document
class ClassDocument(Document):
    class Index:
        name = 'classes'
        settings = _index_settings

    class Django:
        model = m.Class

        # The fields of the model you want to be indexed in Elasticsearch
        fields = [
            'name',
            'abbreviation',
            # 'description',
            'credits',
        ]

        ignore_signals = _ignore_signals
        auto_refresh = _auto_refresh
        queryset_pagination = _queryset_pagination


# @registry.register_document
# class FileDocument(Document):
#     class Index:
#         name = 'files'
#         settings = _index_settings
#
#     class Django:
#         model = m.File
#
#         # The fields of the model you want to be indexed in Elasticsearch
#         fields = [
#             'hash',
#             'name',
#         ]
#
#         ignore_signals = _ignore_signals
#         auto_refresh = _auto_refresh
#         queryset_pagination = _queryset_pagination
