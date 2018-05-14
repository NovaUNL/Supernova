from django.db import transaction, IntegrityError
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import synopses as serializers
from college.models import Class
from synopses import models as synopses


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


class TopicSections(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        serializer = serializers.TopicSectionsSerializer(synopses.Topic.objects.get(id=pk))
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        topic = synopses.Topic.objects.get(id=pk)
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
                synopses.SectionTopic.objects.filter(topic=topic).delete()
                for pair in section_pairs:
                    synopses.SectionTopic(topic=topic, index=pair[0], section_id=pair[1]).save()
        except IntegrityError:
            raise ValidationError("Database transaction failed")


class ClassSections(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        serializer = serializers.ClassSectionsSerializer(synopses.Class.objects.get(id=pk))
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


class Section(APIView):
    def get(self, request, pk, format=None):
        serializer = serializers.SectionSerializer(synopses.Section.objects.get(id=pk))
        return Response(serializer.data)
