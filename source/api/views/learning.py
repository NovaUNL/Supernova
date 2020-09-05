from django.db import transaction, IntegrityError
from django.db.models import F, Max
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import synopses as serializers
from api.serializers.synopses import SectionRelationSerializer
from learning import models as learning
from college import models as college


class Areas(APIView):
    def get(self, request, format=None):
        serializer = serializers.AreaSerializer(learning.Area.objects.all(), many=True)
        return Response(serializer.data)


class Area(APIView):
    def get(self, request, pk, format=None):
        serializer = serializers.AreaSerializer(learning.Area.objects.get(id=pk))
        return Response(serializer.data)


class Subarea(APIView):
    def get(self, request, pk, format=None):
        serializer = serializers.SubareaSerializer(learning.Subarea.objects.get(id=pk))
        return Response(serializer.data)


class Section(APIView):
    def get(self, request, pk, format=None):
        serializer = serializers.SectionSerializer(learning.Section.objects.get(id=pk))
        return Response(serializer.data)


class SectionChildren(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        serializer = SectionRelationSerializer(
            learning.SectionSubsection.objects
                .select_related('section')
                .order_by('index')
                .filter(parent=pk),
            many=True)
        return Response(serializer.data)

    def post(self, request, pk, format=None):
        section = get_object_or_404(learning.Section, id=pk)
        if isinstance(request.data, dict) \
                and 'child' in request.data \
                and isinstance((child_id := request.data['child']), int):

            with transaction.atomic():
                child = get_object_or_404(learning.Section, id=child_id)
                if child in section.children.all():
                    return Response("Ok")
                biggest_index = learning.SectionSubsection.objects \
                    .filter(parent=section) \
                    .annotate(num_books=Max('index')) \
                    .aggregate(Max('index'))['index__max']
                if biggest_index is None:
                    biggest_index = -1
                new = learning.SectionSubsection.objects.create(parent=section, section=child, index=biggest_index + 1)
                return Response(SectionRelationSerializer(new).data)
        raise ValidationError("Bad request")

    def delete(self, request, pk, format=None):
        section = get_object_or_404(learning.Section, id=pk)
        if isinstance(request.data, dict) \
                and 'child' in request.data \
                and isinstance((child_id := request.data['child']), int):
            with transaction.atomic():
                rel = learning.SectionSubsection.objects.filter(parent=section, section_id=child_id).first()
                old_index = rel.index
                learning.SectionSubsection.objects.filter(parent=section, section_id=child_id).delete()
                learning.SectionSubsection.objects \
                    .filter(parent=section, index__gt=old_index) \
                    .update(index=F('index') - 1)
            return Response("Ok")
        raise ValidationError("Bad request")

    def put(self, request, pk, format=None):
        section = get_object_or_404(learning.Section, id=pk)
        section_pairs = []
        try:
            for entry in request.data:
                if not (isinstance(entry['index'], int) and isinstance(entry['id'], int)):
                    raise ValidationError("Invalid data format", code=None)
                section_pairs.append((entry['index'], entry['id']))
        except KeyError:
            raise ValidationError("Invalid data format", code=None)

        section_pairs.sort(key=lambda x: x[0])  # Sort on index
        # Build a map where indexes start on 0 and are sequential:
        indexes = {p[1]: i for i, p in enumerate(section_pairs)}
        try:
            with transaction.atomic():
                mismatches = learning.SectionSubsection.objects \
                    .filter(parent=section) \
                    .exclude(section__in=indexes.keys()) \
                    .order_by('section_id') \
                    .count()
                if mismatches > 0:
                    return Response("Conflict. Mismatched sections.")
                # Set indexes to negative values to avoid integrity errors
                learning.SectionSubsection.objects.filter(parent=section).update(index=-F('index') - 1)
                rels = learning.SectionSubsection.objects.filter(parent=section).order_by('section_id').all()
                for rel in rels:
                    rel.index = indexes[rel.section_id]
                learning.SectionSubsection.objects.bulk_update(rels, ['index'])
        except IntegrityError:
            raise ValidationError("Integrity error")
        return Response("Ok")


class ClassSections(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        serializer = SectionRelationSerializer(
            learning.ClassSection.objects
                .select_related('section')
                .order_by('index')
                .filter(corresponding_class=pk),
            many=True)
        return Response(serializer.data)

    def post(self, request, pk, format=None):
        class_ = get_object_or_404(college.Class, id=pk)
        if isinstance(request.data, dict) \
                and 'child' in request.data \
                and isinstance((child_id := request.data['child']), int):

            with transaction.atomic():
                child = get_object_or_404(learning.Section, id=child_id)
                if child in class_.synopsis_sections.all():
                    return Response("Ok")
                biggest_index = learning.ClassSection.objects \
                    .filter(corresponding_class=class_) \
                    .annotate(num_books=Max('index')) \
                    .aggregate(Max('index'))['index__max']
                if biggest_index is None:
                    biggest_index = -1
                new = learning.ClassSection.objects.create(
                    corresponding_class=class_,
                    section=child,
                    index=biggest_index + 1)
                return Response(SectionRelationSerializer(new).data)
        raise ValidationError("Bad request")

    def delete(self, request, pk, format=None):
        class_ = get_object_or_404(college.Class, id=pk)
        if isinstance(request.data, dict) \
                and 'child' in request.data \
                and isinstance((child_id := request.data['child']), int):
            with transaction.atomic():
                rel = learning.ClassSection.objects.filter(corresponding_class=class_, section_id=child_id).first()
                old_index = rel.index
                learning.ClassSection.objects.filter(corresponding_class=class_, section_id=child_id).delete()
                learning.ClassSection.objects \
                    .filter(corresponding_class=class_, index__gt=old_index) \
                    .update(index=F('index') - 1)
            return Response("Ok")
        raise ValidationError("Bad request")

    def put(self, request, pk, format=None):
        class_ = get_object_or_404(college.Class, id=pk)
        section_pairs = []
        try:
            for entry in request.data:
                if not (isinstance(entry['index'], int) and isinstance(entry['id'], int)):
                    raise ValidationError("Invalid data format", code=None)
                section_pairs.append((entry['index'], entry['id']))
        except KeyError:
            raise ValidationError("Invalid data format", code=None)

        section_pairs.sort(key=lambda x: x[0])  # Sort on index
        # Build a map where indexes start on 0 and are sequential:
        indexes = {p[1]: i for i, p in enumerate(section_pairs)}
        try:
            with transaction.atomic():
                mismatches = learning.ClassSection.objects \
                    .filter(corresponding_class=class_) \
                    .exclude(section__in=indexes.keys()) \
                    .order_by('section_id') \
                    .count()
                if mismatches > 0:
                    return Response("Conflict. Mismatched sections.")
                # Set indexes to negative values to avoid integrity errors
                learning.ClassSection.objects.filter(corresponding_class=class_).update(index=-F('index') - 1)
                rels = learning.ClassSection.objects.filter(corresponding_class=class_).order_by('section_id').all()
                for rel in rels:
                    rel.index = indexes[rel.section_id]
                learning.ClassSection.objects.bulk_update(rels, ['index'])
        except IntegrityError:
            raise ValidationError("Integrity error")
        return Response("Ok")
