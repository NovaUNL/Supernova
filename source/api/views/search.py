from elasticsearch_dsl import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response
from college import documents as college_search
from learning import documents as learning_search
from groups import documents as groups_search
from services import documents as services_search
from news import documents as news_search
from api import serializers

mapping = {
    'teacher': {
        'class': college_search.TeacherDocument,
        'serializer': serializers.college.TeacherSerializer,
        'fields': ['name', 'abbreviation'],
        'private': True
    },
    'student': {
        'class': college_search.StudentDocument,
        'serializer': serializers.college.StudentSerializer,
        'fields': ['name', 'abbreviation'],  # TODO number
        'private': True
    },
    'group': {
        'class': groups_search.GroupDocument,
        'serializer': serializers.groups.GroupMinimalSerializer,
        'fields': ['title', 'abbreviation', 'content'],
        'private': False
    },
    'building': {
        'class': college_search.BuildingDocument,
        'serializer': serializers.college.BuildingSerializer,
        'fields': ['name', 'abbreviation'],
        'private': False
    },
    'room': {
        'class': college_search.RoomDocument,
        'serializer': serializers.college.RoomSerializer,
        'fields': ['name', ],
        'private': False
    },
    'class': {
        'class': college_search.ClassDocument,
        'serializer': serializers.college.ClassSerializer,
        'fields': ['name', 'abbreviation'],
        'private': False
    },
    'course': {
        'class': college_search.CourseDocument,
        'serializer': serializers.college.CourseSerializer,
        'fields': ['name', 'abbreviation'],
        'private': False
    },
    'department': {
        'class': college_search.DepartmentDocument,
        'serializer': serializers.college.DepartmentSerializer,
        'fields': ['name', 'description'],
        'private': False
    },
    'service': {
        'class': services_search.ServiceDocument,
        'serializer': serializers.services.ServiceSerializer,
        'fields': ['name'],
        'private': False
    },
    'synopsis': {
        'class': learning_search.SectionDocument,
        'serializer': serializers.learning.SectionPreviewSerializer,
        'fields': ['title', 'content'],
        'private': False
    },
    'exercise': {
        'class': learning_search.ExerciseDocument,
        'serializer': serializers.learning.ExercisePreviewSerializer,
        'fields': ['content'],
        'private': False
    },
    'question': {
        'class': learning_search.QuestionDocument,
        'serializer': serializers.learning.QuestionSerializer,
        'fields': ['title', 'content', 'answers'],
        'private': False
    },
    'news': {
        'class': news_search.NewsItemDocument,
        'serializer': serializers.news.NewsMinimalSerializer,
        'fields': ['title', 'content'],
        'private': False
    },
}


@api_view(['GET'])
def search_view(request):
    q = request.GET.get('q')
    e = request.GET.get('e')
    if q is None or (e is not None and e not in mapping):
        return Response({'results': []})
    private_access = not request.user.is_anonymous and request.user.has_perm('users.student_access')

    results = dict()
    if e:
        doc_search = mapping[e]
        if doc_search['private'] and not private_access:
            return Response({'error': 'This data class is private'}, status=403)

        qs = doc_search['class'].search() \
            .query(Q("multi_match", query=q, fields=doc_search['fields'])) \
            .to_queryset()
        serialized = doc_search['serializer'](qs, many=True)
        if len(serialized.data):
            results[e] = serialized.data
    else:
        for key, doc_search in mapping.items():
            if doc_search['private'] and not private_access:
                continue
            qs = doc_search['class'].search() \
                .query(Q("multi_match", query=q, fields=doc_search['fields'])) \
                .to_queryset()
            serialized = doc_search['serializer'](qs, many=True)
            if len(serialized.data):
                results[key] = serialized.data

    return Response({'results': results})
