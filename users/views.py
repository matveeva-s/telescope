from rest_framework import viewsets, generics
from rest_framework.response import Response

from users.models import Profile
from users.serializers import UserProfileSerializer


class ProfileView(generics.UpdateAPIView):
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=self.request.data, context=self.get_serializer_context())
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        data = serializer.data
        first_name = data.pop('first_name')
        last_name = data.pop('last_name')
        email = data.pop('email')
        print(data)
        print(serializer.data)
        self.get_queryset().update(**data)
        self.request.user.first_name = first_name
        self.request.user.last_name = last_name
        self.request.user.email = email
        self.request.user.save()
        return Response(data='Профиль успешно обновлен')
