import pdb

from django.contrib.auth import authenticate
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from game.models import Game, Country, Territory, Unit, Turn, Order
from game.serializers import UserSerializer, GameSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token


# this all isn't necessary currently but will become useful again with
# the incorporation of React-Router-Redux

# class Login(ObtainAuthToken):

#     def post(self, request, *args, **kwargs):
#         serializer = self.serializer_class(data=request.data,
#                                            context={'request': request})
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data['user']
#         token, created = Token.objects.get_or_create(user=user)
#         return Response({
#             'token': token.key,
#             'first_name': user.first_name,
#             'last_name': user.last_name,
#             'email': user.email,
#             'games': [{'id': x.id,
#                        'title': x.title,
#                        'created_at': x.created_at
#                        } for x in user.games.all()]
#         })


class Sessions(APIView):
    """
    Return a user's data if they have a valid token.
    """

    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UsersList(APIView):
    """
    Create a new user, receive back that user's token.
    """

    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = Token.objects.get(user=user)
            return Response({'token': token.key},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
