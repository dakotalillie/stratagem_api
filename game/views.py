from django.http import Http404
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

from . import models
from . import serializers
from . import constants
from . import utils


import pdb


class Sandbox(APIView):
    """
    Create a new sandbox game
    """

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        country_players = {country: request.user for country in
                           constants.COUNTRY_NAMES}
        game = models.Game(title='New Sandbox')
        game.save(country_players=country_players)
        game.initialize_units()
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
            return models.Game.objects.get(pk=pk)
        except models.Game.DoesNotExist:
            raise Http404

    def get(self, request, pk):
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

    def get_game(self, pk):
        try:
            return models.Game.objects.get(pk=pk)
        except models.Game.DoesNotExist:
            raise Http404

    def post(self, request, pk):
        game = self.get_game(pk)
        data = utils.dict_keys_to_snake_case(request.data)
        turn_processor = TurnProcessor.get_turn_processor(game, data)
        turn_processor.process_turn()
        serializer = serializers.GameDetailSerializer(game)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        pass
