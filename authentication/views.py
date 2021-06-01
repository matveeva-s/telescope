from django.http import JsonResponse

from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status, permissions
from rest_framework.response import Response

from telescope.settings import SITE_URL, MEDIA_URL


class LogoutAndBlacklistRefreshTokenForUserView(APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def post(self, request):
        try:
            refresh_token = request.data['refresh_token']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserData(APIView):

    def get(self, request):
        user = request.user

        return JsonResponse({
            'firstName': user.first_name,
            'lastName': user.last_name,
            'avatar': f'{SITE_URL}{MEDIA_URL}{user.profile.avatar}',
            'email': user.email,
            'gender': user.profile.gender,
            'company': user.profile.company,
            'position': user.profile.position,
        })
