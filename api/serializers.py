import datetime

from rest_framework import serializers

from kleep.models import Class, Course, BarDailyMenu


class DegreeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class BuildingMinimalSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    abbreviation = serializers.CharField(required=False)


class ServiceSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(required=True)
    opening = serializers.IntegerField(required=False)
    lunch_start = serializers.IntegerField(required=False)
    lunch_end = serializers.IntegerField(required=False)
    closing = serializers.IntegerField(required=False)


class ServiceWithBuildingSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(required=True)
    opening = serializers.IntegerField(required=False)
    lunch_start = serializers.IntegerField(required=False)
    lunch_end = serializers.IntegerField(required=False)
    closing = serializers.IntegerField(required=False)
    building = BuildingMinimalSerializer()


class BuildingUsageSerializer(serializers.Serializer):
    usage = serializers.CharField()
    url = serializers.CharField()
    relevant = serializers.BooleanField()


class BuildingWithServicesSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    abbreviation = serializers.CharField(required=False)
    services = ServiceSerializer(many=True, source='service_set')
    usages = BuildingUsageSerializer(many=True, source='buildingusage_set')


class ClassMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ('id', 'name')


class CourseMinimalSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    abbreviation = serializers.CharField()
    degree = DegreeSerializer()


class DepartmentMinimalSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class CourseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    abbreviation = serializers.CharField()
    description = serializers.CharField()
    department = DepartmentMinimalSerializer()
    degree = DegreeSerializer()
    url = serializers.CharField()


class DepartmentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    building = BuildingMinimalSerializer()
    class_set = ClassMinimalSerializer(many=True)
    course_set = CourseMinimalSerializer(many=True)


class ClassSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    abbreviation = serializers.CharField()
    credits = serializers.IntegerField()
    department = DepartmentMinimalSerializer()


class GroupMinimalSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    abbreviation = serializers.CharField()


class GroupTypeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    type = serializers.CharField()
    group_set = GroupMinimalSerializer(many=True)


class StoreItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    price = serializers.IntegerField()
    stock = serializers.IntegerField()
    seller = GroupMinimalSerializer()


class SynopsisTopicSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class SynopsisSubareaSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    synopsistopic_set = SynopsisTopicSerializer(many=True)


class SynopsisAreaSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    synopsissubarea_set = SynopsisSubareaSerializer(many=True)


class SynopsisSectionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class SynopsisTopicSectionsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    synopsissection_set = SynopsisSectionSerializer(many=True)


class BarPriceSerializer(serializers.Serializer):
    item = serializers.CharField()
    price = serializers.IntegerField()


class TodaysMenuFilteredListSerializer(serializers.ListSerializer):

    def to_representation(self, data):
        # data = data.filter(date__gte=datetime.datetime.today())  # TODO apply filter whenever this gets deployed
        return super(TodaysMenuFilteredListSerializer, self).to_representation(data)


class TodaysBarMenuSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('item', 'price')
        list_serializer_class = TodaysMenuFilteredListSerializer
        model = BarDailyMenu


class BarListMenusSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='service.id')
    name = serializers.CharField(source='service.name')
    prices = BarPriceSerializer(many=True, source='barprice_set')
    menu = TodaysBarMenuSerializer(source='bardailymenu_set', many=True)


class StudentSerializer(serializers.Serializer):
    abbreviation = serializers.CharField()
    number = serializers.IntegerField()
    course = CourseMinimalSerializer()


class ProfileMinimalSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    nickname = serializers.CharField()


class ProfileDetailedSerializer(serializers.Serializer):
    nickname = serializers.CharField()
    name = serializers.CharField()
    student_set = StudentSerializer(many=True)


class NewsMinimalSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    summary = serializers.CharField()
    datetime = serializers.DateTimeField()


class NewsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    summary = serializers.CharField()
    content = serializers.CharField()
    datetime = serializers.DateTimeField()
    author = ProfileMinimalSerializer()
