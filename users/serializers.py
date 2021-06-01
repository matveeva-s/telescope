from rest_framework import serializers
from users.models import Profile


class UserProfileSerializer(serializers.ModelSerializer):
    last_name = serializers.CharField(source='user.last_name')
    first_name = serializers.CharField(source='user.first_name')
    email = serializers.CharField(source='user.email')
    company = serializers.CharField(source='company.name')
    avatar = serializers.CharField(allow_blank=True)

    class Meta:
        model = Profile
        fields = ('avatar', 'company', 'gender', 'position', 'email', 'last_name', 'first_name')
