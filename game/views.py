from django.shortcuts import render
from rest_framework.views import APIView
from game.models import Game, Country, Territory, Unit, Turn, Order


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
