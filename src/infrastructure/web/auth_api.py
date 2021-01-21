import datetime as dt
import logging

from django.contrib.auth import login
from drfpasswordless.views import ObtainAuthTokenFromCallbackToken
from rest_framework import status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class BaseAPIView(APIView):
    @classmethod
    def as_view(cls, **initkwargs):
        """
        Store the original class on the view function.

        This allows us to discover information about the view when we do URL
        reverse lookups.  Used for breadcrumb generation.
        """
        view = super().as_view(**initkwargs)
        view.cls = cls
        view.initkwargs = initkwargs

        # Note: session based authentication is explicitly CSRF validated,
        # all other authentication is CSRF exempt.
        return view


class GetAuthTokenCookie(ObtainAuthToken):
    authentication_classes = []
    permission_classes = ()

    def get(self, request, *args, **kwargs):
        print(request.COOKIES)
        token = request.COOKIES.get('token')
        if token:
            token = Token.objects.get(key=token)
            user = token.user

            return Response({
                'token': token.key,
                'user_id': user.pk,
                'email': user.email
            })
        return Response({'status': 'not authorized'}, status=403)


class DashboardEmailAuthorization(ObtainAuthTokenFromCallbackToken):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']
            token = Token.objects.get_or_create(user=user)[0]

            if token:
                # Return our key for consumption.
                response = Response({'token': token.key}, status=status.HTTP_200_OK)
                response.set_cookie(
                    'token',
                    path='/',
                    httponly=True,
                    value=token.key,
                    expires=dt.datetime.utcnow() + dt.timedelta(days=30)
                )
                return response
        else:
            logger.error("Couldn't log in unknown user. Errors on serializer: {}".format(serializer.error_messages))
        return Response({'detail': 'Couldn\'t log you in. Try again later.'}, status=status.HTTP_400_BAD_REQUEST)


class TokenLogoutAPI(APIView):
    def get(self, request, *args, **kwargs):
        response = Response({'success': True}, status=status.HTTP_200_OK)
        response.delete_cookie('token', path='/')
        return response

