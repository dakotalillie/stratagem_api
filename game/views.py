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
        game = Game(title='New Sandbox')
        countries = {c: Country(name=c, game=game, user=request.user)
                     for c in constants.COUNTRY_NAMES}
        turn = Turn(year=1901, season='spring', phase='diplomatic', game=game)

        with open('game/data/countries.json') as countries_json:
            country_data = json.loads(countries_json.read())

        with open('game/data/territories.json') as territories_json:
            territories_data = json.loads(territories_json.read())

        territories = {}
        units = {}

        for country, data in country_data.items():
            for terr_abbr in data['startingTerritories']:
                terr = Territory(name=territories_data[terr_abbr]['name'],
                                 abbreviation=terr_abbr,
                                 owner=countries[country], game=game)
                territories[terr_abbr] = terr
            for unit_dict in data['startingUnits']:
                unit = Unit(unit_type=unit_dict['type'],
                            country=countries[country],
                            territory=territories[unit_dict['territory']],
                            coast=unit_dict['coast'], game=game)
                units[unit.territory.abbreviation] = unit

        for terr_abbr, terr_data in territories_data.items():
            if terr_abbr not in territories:
                terr = Territory(
                    name=terr_data['name'], abbreviation=terr_abbr, game=game)
                territories[terr_abbr] = terr

        game.save()
        for country_name, country in countries.items():
            country.save()
        turn.save()
        for terr_abbr, territory in territories.items():
            territory.save()
        for terr_abbr, unit in units.items():
            unit.save()

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
        game = Game.objects.get(pk=pk)
        retreat_phase_necessary = False
        if game.current_turn().phase == 'diplomatic':
            orders = [utils.create_order_from_data(data)
                      for unit_id, data in request.data['orders'].items()]
            utils.create_missing_hold_orders(game, orders)
            convoy_routes = [utils.map_convoy_route_to_models(route)
                             for route in request.data['convoy_routes']]
            locations, supports, conflicts = utils.map_orders_to_locations(
                orders)
            displaced_units = []
            # Convoy routes need to be resolved first, because if
            # there's a unit providing support in the territory that the
            # convoyed unit is moving to, that support could be cut.
            while len(convoy_routes) > 0:
                convoy_route = convoy_routes.pop(0)
                other_routes = utils.more_possible_convoy_routes(convoy_routes,
                                                                 convoy_route)
                resolved = utils.resolve_conflicts_in_convoy_route(
                    convoy_route, locations, supports, conflicts,
                    displaced_units, other_routes
                )
                if not resolved:
                    convoy_routes.append(convoy_route)
            utils.add_supports(locations, supports, conflicts)
            utils.check_for_illegal_swaps(orders, locations, conflicts)
            while len(conflicts) > 0:
                conflict_location = conflicts.pop()
                utils.resolve_conflict(conflict_location, locations, conflicts,
                                       displaced_units)

            utils.update_unit_locations(locations, displaced_units, orders)
            retreat_phase_necessary = len(displaced_units) > 0
        elif game.current_turn().phase == 'retreat':
            orders = [utils.create_retreat_order_from_data(data, game)
                      for unit_id, data in request.data['orders'].items()]
            utils.create_missing_delete_orders(game, orders)
            locations = utils.handle_retreat_conflicts(orders)
            utils.update_retreat_unit_locations(locations, orders)
        elif game.current_turn().phase == 'reinforcement':
            for territory, order_data in request.data['orders'].items():
                utils.create_reinforcement_order_from_data(order_data, game)
        # CREATE NEW CURRENT TURN
        utils.create_new_turn(game.current_turn(), retreat_phase_necessary)
        if game.current_turn().phase == 'reinforcement':
            utils.update_territory_owners(game)
        serializer = serializers.GameDetailSerializer(game)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk, format=None):
        pass
