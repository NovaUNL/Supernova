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
from college.models import Class
from synopses import models as synopses
from college import models as college


class Areas(APIView):
    def get(self, request, format=None):
        serializer = serializers.AreaSerializer(synopses.Area.objects.all(), many=True)
        return Response(serializer.data)


class Area(APIView):
    def get(self, request, pk, format=None):
        serializer = serializers.AreaSerializer(synopses.Area.objects.get(id=pk))
        return Response(serializer.data)


class Subarea(APIView):
    def get(self, request, pk, format=None):
        serializer = serializers.SubareaSerializer(synopses.Subarea.objects.get(id=pk))
        return Response(serializer.data)


class Section(APIView):
    def get(self, request, pk, format=None):
        serializer = serializers.SectionSerializer(synopses.Section.objects.get(id=pk))
        return Response(serializer.data)


class SectionChildren(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        serializer = SectionRelationSerializer(
            synopses.SectionSubsection.objects
                .select_related('section')
                .order_by('index')
                .filter(parent=pk),
            many=True)
        return Response(serializer.data)

    def post(self, request, pk, format=None):
        section = get_object_or_404(synopses.Section, id=pk)
        if isinstance(request.data, dict) \
                and 'child' in request.data \
                and isinstance((child_id := request.data['child']), int):

            with transaction.atomic():
                child = get_object_or_404(synopses.Section, id=child_id)
                if child in section.children:
                    return Response("Ok")
                biggest_index = synopses.SectionSubsection.objects \
                    .filter(parent=section) \
                    .annotate(num_books=Max('index')) \
                    .aggregate(Max('index'))['index__max']
                if biggest_index is None:
                    biggest_index = -1
                new = synopses.SectionSubsection.objects.create(parent=section, section=child, index=biggest_index + 1)
                return Response(SectionRelationSerializer(new).data)
        raise ValidationError("Bad request")

    def delete(self, request, pk, format=None):
        section = get_object_or_404(synopses.Section, id=pk)
        if isinstance(request.data, dict) \
                and 'child' in request.data \
                and isinstance((child_id := request.data['child']), int):
            with transaction.atomic():
                rel = synopses.SectionSubsection.objects.filter(parent=section, section_id=child_id).first()
                old_index = rel.index
                synopses.SectionSubsection.objects.filter(parent=section, section_id=child_id).delete()
                synopses.SectionSubsection.objects\
                    .filter(parent=section, section_id=child_id, index__gt=old_index)\
                    .update(F('index') - 1)
            return Response("Ok")
        raise ValidationError("Bad request")

    def put(self, request, pk, format=None):
        section = get_object_or_404(synopses.Section, id=pk)
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
                mismatches = synopses.SectionSubsection.objects \
                    .filter(parent=section) \
                    .exclude(section__in=indexes.keys()) \
                    .order_by('section_id') \
                    .count()
                if mismatches > 0:
                    return Response("Conflict. Mismatched sections.")
                # Set indexes to negative values to avoid integrity errors
                synopses.SectionSubsection.objects.filter(parent=section).update(index=-F('index'))
                rels = synopses.SectionSubsection.objects.filter(parent=section).order_by('section_id').all()
                for rel in rels:
                    rel.index = indexes[rel.section_id]
                synopses.SectionSubsection.objects.bulk_update(rels, ['index'])
        except IntegrityError:
            raise ValidationError("Integrity error")
        return Response("Ok")


class ClassSections(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        serializer = serializers.ClassSectionsSerializer(college.Class.objects.get(id=pk))
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        synopsis_class = Class.objects.get(id=pk)
        section_pairs = []
        try:
            for entry in request.data:
                if not (isinstance(entry['index'], int) and isinstance(entry['id'], int)):
                    raise ValidationError("Invalid data format", code=None)
                content = (entry['index'], entry['id'])
                section_pairs.append(content)
        except KeyError:
            raise ValidationError("Invalid data format", code=None)
        section_pairs.sort(key=lambda x: x[0])

        if len(section_pairs) == 0:
            # Delete everything, require confirmation since client-side code can have errors and users are silly
            return Response("Not so soon")  # TODO implement

        index = 0
        sections = set()
        for pair in section_pairs:
            if pair[0] != index:
                raise ValidationError("Missing indexes")
            index += 1
            if pair[1] in sections:
                raise ValidationError("Duplicated sections")
            sections.add(pair[1])

        try:
            with transaction.atomic():
                synopses.ClassSection.objects.filter(corresponding_class=synopsis_class).delete()
                for pair in section_pairs:
                    synopses.ClassSection(corresponding_class=synopsis_class, index=pair[0], section_id=pair[1]).save()
        except IntegrityError:
            raise ValidationError("Database transaction failed")
