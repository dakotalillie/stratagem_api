import pdb
import json

from django.http import Http404
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Game, Country, Territory, Unit, Turn, Order
from . import serializers
from . import utils
from . import constants


@api_view(['GET'])
def current_user(request):
    """
    Determine the current user by their token, and return their data
    """
    serializer = serializers.UserSerializer(request.user)
    return Response(serializer.data)


class UserList(APIView):
    """
    Create a new user, receive back that user's token.
    """

    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = serializers.UserSerializerWithToken(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Sandbox(APIView):
    """
    Create a new sandbox game
    """

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        country_players = {country: request.user for country in
                           constants.COUNTRY_NAMES}
        game = Game(title='New Sandbox')
        game.save(country_players=country_players)
        return Response({'game_id': game.id}, status=status.HTTP_201_CREATED)


class GameList(APIView):
    """
    List all games belonging to a particular player, or create a new game.
    """

    def get(self, request, format=None):
        pass

    def post(self, request, format=None):
        pass


class GameDetail(APIView):
    """
    Retrieve, update, and delete games.
    """

    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, pk):
        try:
            return Game.objects.get(pk=pk)
        except Snippet.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        game = self.get_object(pk)
        serializer = serializers.GameDetailSerializer(game)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        pass

    def delete(self, request, pk, format=None):
        pass


class OrderList(APIView):
    """
    Create and delete orders in batches
    """

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk, format=None):
        params = {
            'game':                    Game.objects.get(pk=pk),
            'request_data':            request.data,
            'retreat_phase_necessary': False
        }
        if game.current_turn().phase == 'diplomatic':
            utils.diplomatic_utils.process_diplomatic_turn(params)
        elif game.current_turn().phase == 'retreat':
            utils.retreat_utils.process_retreat_turn(params)
        elif game.current_turn().phase == 'reinforcement':
            utils.reinforcement_utils.process_reinforcement_turn(params)
        utils.update_turn_utils.update_turn(params)
        serializer = serializers.GameDetailSerializer(params['game'])
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk, format=None):
        pass
