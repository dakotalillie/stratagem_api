import pdb

from django.contrib.auth import authenticate
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from game.models import Game, Country, Territory, Unit, Turn, Order
from game.serializers import UserSerializer, GameSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token


class Login(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'games': [{'id': x.id,
                       'title': x.title,
                       'created_at': x.created_at
                       } for x in user.games.all()]
        })


class Sessions(APIView):
    """
    Either create a new session given a valid username and password, or
    confirm that the user is logged in.
    """

    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        pass

    def post(self, request, format=None):
        user = authenticate(username=request.data['username'],
                            password=request.data['password'])
        if user is not None:
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid login credentials'},
                            status=status.HTTP_401_UNAUTHORIZED)


class GamesList(APIView):
    """
    List all games belonging to a particular player, or create a new game.
    """

    def get(self, request, format=None):
        pass

    def post(self, request, format=None):
        pass


class GamesDetail(APIView):
    """
    Retrieve, update, and delete games.
    """

    def get(self, request, pk, format=None):
        pass

    def put(self, request, pk, format=None):
        pass

    def delete(self, request, pk, format=None):
        pass


class OrdersList(APIView):
    """
    Create and delete orders in batches
    """

    def post(self, request, pk, format=None):
        pass

    def delete(self, request, pk, format=None):
        pass
