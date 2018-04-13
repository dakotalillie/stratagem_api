import pdb
import json

from django.contrib.auth import authenticate
from django.http import Http404
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from game.models import Game, Country, Territory, Unit, Turn, Order
from game.serializers import UserSerializer, GameDetailSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from . import utils


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


class Sandbox(APIView):
    """
    Create a new sandbox game
    """

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        game = Game(title='New Sandbox')
        country_names = ['Austria', 'England', 'France', 'Germany', 'Italy',
                         'Russia', 'Turkey']
        countries = {c: Country(name=c, game=game, user=request.user)
                     for c in country_names}
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

    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, pk):
        try:
            return Game.objects.get(pk=pk)
        except Snippet.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        game = self.get_object(pk)
        serializer = GameDetailSerializer(game)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        pass

    def delete(self, request, pk, format=None):
        pass


class OrdersList(APIView):
    """
    Create and delete orders in batches
    """

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk, format=None):
        orders = [utils.create_order_from_data(data)
                  for unit_id, data in request.data['orders'].items()]
        convoy_routes = [utils.map_convoy_route_to_models(route)
                         for route in request.data['convoy_routes']]
        locations, supports, conflicts = utils.map_orders_to_locations(orders)
        displaced_units = []
        # Convoy routes need to be resolved first, because if there's a unit
        # providing support in the territory that the convoyed unit is moving
        # to, that support could be cut.
        while len(convoy_routes) > 0:
            convoy_route = convoy_routes.pop(0)
            other_routes = utils.more_possible_convoy_routes(convoy_routes,
                                                             convoy_route)
            resolved = utils.resolve_conflicts_in_convoy_route(
                convoy_route, locations, supports, conflicts, displaced_units,
                other_routes
            )
            if not resolved:
                convoy_routes.append(convoy_route)

        utils.add_supports(locations, supports)
        while len(conflicts) > 0:
            conflict_location = conflicts.pop()
            utils.resolve_conflict(conflict_location, locations, conflicts,
                                   displaced_units)

        pdb.set_trace()

    def delete(self, request, pk, format=None):
        pass
