from rest_framework import serializers
from tasks.models import Telescope, Balance


def converting_degrees(value):
    degrees = abs(int(value))
    minutes = abs(value - degrees) * 60
    seconds = int(abs(minutes - int(minutes)) * 60)
    minutes = int(minutes)
    return degrees, minutes, seconds


class TelescopeSerializer(serializers.ModelSerializer):
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    balance = serializers.SerializerMethodField()

    def get_latitude(self, obj):
        deg, min, sec = converting_degrees(obj.latitude)
        place = 'N' if obj.latitude > 0 else 'S'
        return f'{deg}°{min}\'{sec}\" {place}'

    def get_longitude(self, obj):
        deg, min, sec = converting_degrees(obj.longitude)
        place = 'E' if obj.longitude > 0 else 'W'
        return f'{deg}°{min}\'{sec}\" {place}'

    def get_status(self, obj):
        return obj.get_status_display()

    def get_balance(self, obj):
        return obj.get_user_balance(self.context['request'].user)

    class Meta:
        model = Telescope
        fields = ('id', 'name', 'avatar', 'status', 'description', 'location', 'latitude', 'longitude', 'balance')


class TelescopeBalanceSerializer(serializers.ModelSerializer):
    value = serializers.CharField(source='id')
    label = serializers.CharField(source='name')
    balance = serializers.SerializerMethodField()

    def get_balance(self, obj):
        return obj.get_user_balance(self.context['request'].user)

    class Meta:
        model = Telescope
        fields = ('label', 'value', 'balance')
