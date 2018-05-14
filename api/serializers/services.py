from rest_framework import serializers

from api.serializers.college import BuildingSerializer
from services.models import MenuDish


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
    building = BuildingSerializer()


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
        model = MenuDish


class BarListMenusSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='service.id')
    name = serializers.CharField(source='service.name')
    prices = BarPriceSerializer(many=True, source='barprice_set')
    menu = TodaysBarMenuSerializer(source='bardailymenu_set', many=True)
