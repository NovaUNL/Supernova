from django.conf import settings
from django_elasticsearch_dsl import Document, TextField
from django_elasticsearch_dsl.registries import registry
from college import models as m


@registry.register_document
class StudentDocument(Document):
    class Index:
        name = 'students'
        settings = settings.ELASTIC_INDEX_SETTINGS

    class Django:
        model = m.Student
        fields = ['name', 'number', 'abbreviation', 'year', 'first_year', 'last_year']
        ignore_signals = settings.ELASTIC_IGNORE_SIGNALS
        auto_refresh = settings.ELASTIC_AUTO_REFRESH
        queryset_pagination = settings.ELASTIC_QUERYSET_PAGINATION


@registry.register_document
class TeacherDocument(Document):
    class Index:
        name = 'teachers'
        settings = settings.ELASTIC_INDEX_SETTINGS

    class Django:
        model = m.Teacher
        fields = ['name', 'abbreviation', 'first_year', 'last_year']
        ignore_signals = settings.ELASTIC_IGNORE_SIGNALS
        auto_refresh = settings.ELASTIC_AUTO_REFRESH
        queryset_pagination = settings.ELASTIC_QUERYSET_PAGINATION


@registry.register_document
class BuildingDocument(Document):
    class Index:
        name = 'buildings'
        settings = settings.ELASTIC_INDEX_SETTINGS

    class Django:
        model = m.Building
        fields = ['name', 'abbreviation']
        ignore_signals = settings.ELASTIC_IGNORE_SIGNALS
        auto_refresh = settings.ELASTIC_AUTO_REFRESH
        queryset_pagination = settings.ELASTIC_QUERYSET_PAGINATION


@registry.register_document
class DepartmentDocument(Document):
    description = TextField()

    def prepare_description(self, instance):
        # TODO remove markdown
        return str(instance.description)

    class Index:
        name = 'departments'
        settings = settings.ELASTIC_INDEX_SETTINGS

    class Django:
        model = m.Department
        fields = ['name']
        ignore_signals = settings.ELASTIC_IGNORE_SIGNALS
        auto_refresh = settings.ELASTIC_AUTO_REFRESH
        queryset_pagination = settings.ELASTIC_QUERYSET_PAGINATION


@registry.register_document
class RoomDocument(Document):
    class Index:
        name = 'rooms'
        settings = settings.ELASTIC_INDEX_SETTINGS

    class Django:
        model = m.Room
        fields = ['name', 'floor', 'description', 'door_number']
        ignore_signals = settings.ELASTIC_IGNORE_SIGNALS
        auto_refresh = settings.ELASTIC_AUTO_REFRESH
        queryset_pagination = settings.ELASTIC_QUERYSET_PAGINATION


@registry.register_document
class CourseDocument(Document):
    description = TextField()

    def prepare_description(self, instance):
        # TODO remove markdown
        return str(instance.description)

    class Index:
        name = 'course'
        settings = settings.ELASTIC_INDEX_SETTINGS

    class Django:
        model = m.Course
        fields = ['name', 'abbreviation']
        ignore_signals = settings.ELASTIC_IGNORE_SIGNALS
        auto_refresh = settings.ELASTIC_AUTO_REFRESH
        queryset_pagination = settings.ELASTIC_QUERYSET_PAGINATION


@registry.register_document
class ClassDocument(Document):
    description = TextField()

    def prepare_description(self, instance):
        # TODO remove markdown
        return str(instance.description)

    class Index:
        name = 'classes'
        settings = settings.ELASTIC_INDEX_SETTINGS

    class Django:
        model = m.Class
        fields = ['name', 'abbreviation', 'credits']
        ignore_signals = settings.ELASTIC_IGNORE_SIGNALS
        auto_refresh = settings.ELASTIC_AUTO_REFRESH
        queryset_pagination = settings.ELASTIC_QUERYSET_PAGINATION


@registry.register_document
class FileDocument(Document):
    names = TextField()

    def prepare_names(self, instance):
        if instance.meta is None:
            instance.analyse()
        names = set(filter(lambda n: n, instance.class_files.values_list('name', flat=True)))
        if len(names):
            return " ".join(names)

    class Index:
        name = 'files'
        settings = settings.ELASTIC_INDEX_SETTINGS

    class Django:
        model = m.File
        fields = ['hash', 'name']
        ignore_signals = settings.ELASTIC_IGNORE_SIGNALS
        auto_refresh = settings.ELASTIC_AUTO_REFRESH
        queryset_pagination = settings.ELASTIC_QUERYSET_PAGINATION
