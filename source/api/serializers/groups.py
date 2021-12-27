from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer
from groups import models as m


class GroupSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    abbreviation = serializers.CharField()
    type = serializers.IntegerField()
    outsider_openness = serializers.IntegerField()
    official = serializers.BooleanField()
    url = serializers.CharField(source='get_absolute_url')
    thumb = serializers.URLField(source='thumbnail_or_default')


class EventSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    group = serializers.PrimaryKeyRelatedField(read_only=True)
    title = serializers.CharField()
    description = serializers.CharField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    time = serializers.TimeField()
    duration = serializers.IntegerField()
    revoked = serializers.BooleanField()
    place = serializers.PrimaryKeyRelatedField(read_only=True)
    capacity = serializers.IntegerField()
    cost = serializers.IntegerField()
    type = serializers.IntegerField()


class GallerySerializer(serializers.Serializer):
    title = serializers.CharField()
    index = serializers.IntegerField()


class GalleryItemSerializer(serializers.Serializer):
    pass


class AnnouncementSerializer(serializers.Serializer):
    group = serializers.PrimaryKeyRelatedField(read_only=True)
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    datetime = serializers.DateTimeField()
    title = serializers.CharField()
    content = serializers.CharField()


class EventAnnouncementSerializer(serializers.Serializer):
    group = serializers.PrimaryKeyRelatedField(read_only=True)
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    datetime = serializers.DateTimeField()
    event = EventSerializer()


class GalleryUploadSerializer(serializers.Serializer):
    group = serializers.PrimaryKeyRelatedField(read_only=True)
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    datetime = serializers.DateTimeField()
    item = GalleryItemSerializer()


class PublicGroupActivitySerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        m.Announcement: AnnouncementSerializer,
        m.EventAnnouncement: EventAnnouncementSerializer,
        m.GalleryUpload: GalleryUploadSerializer,
    }


class ScheduleOnceSerializer(serializers.Serializer):
    title = serializers.CharField()
    datetime = serializers.DateTimeField()
    duration = serializers.IntegerField()
    revoked = serializers.BooleanField()


class SchedulePeriodicSerializer(serializers.Serializer):
    title = serializers.CharField()
    weekday = serializers.IntegerField()
    time = serializers.TimeField()
    duration = serializers.IntegerField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    revoked = serializers.BooleanField()


class ScheduleEntriesSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        m.ScheduleOnce: ScheduleOnceSerializer,
        m.SchedulePeriodic: SchedulePeriodicSerializer
    }


class RelatedGroupSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    abbreviation = serializers.CharField()
    url = serializers.CharField(source='get_absolute_url')
    thumb = serializers.URLField(source='thumbnail_or_default')

    activities = PublicGroupActivitySerializer(source='public_activity', many=True)
    schedule_entries = ScheduleEntriesSerializer(many=True)
    events = EventSerializer(many=True)
