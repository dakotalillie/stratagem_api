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
from game.utils import create_order_from_data
from game.utils import map_convoy_route_to_models


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
        orders = [create_order_from_data(data)
                  for unit_id, data in request.data['orders'].items()]
        convoy_routes = [map_convoy_route_to_models(route)
                         for route in request.data['convoy_routes']]
        conflicts = set([])
        locations = {}
        displaced_units = []

        for order in orders:
            # CASE: no moves recorded for this territory yet
            if order.destination not in locations:
                locations[order.destination] = {order.unit: 1}
            # CASE: other unit(s) attempting to occupy territory
            else:
                locations[order.destination][order.unit] = 1
                conflicts.add(order.destination)
            # Hold on to to supports, so we can factor them in later.
            if order.order_type != 'support':
                orders.remove(order)

        # Convoy routes need to be resolved first, because if there's a unit
        # providing support in the territory that the convoyed unit is moving
        # to, that support could be cut.
        for convoy_route in convoy_routes:
            for convoyeur in convoy_route:
                if convoyeur.territory in conflicts:
                    # Resolve conflict.
                    units_in_convoyeur_terr = locations[convoyeur.territory]
                    for unit, strength in units_in_convoyeur_terr.items():
                        # Find all supports for that unit.
                        unit_supports = filter(
                            lambda x: x.order_type == 'support' and
                            x.aux_unit is unit, orders
                        )
                        # Check to make sure supports haven't been cut,
                        # including checking to make sure support isn't being
                        # cut from the convoy origin.
                        for support_order in unit_supports:
                            if (support_order.origin not in conflicts or
                                    locations[support_order.origin].keys == [
                                        support_order.unit,
                                        convoy_route.unit
                                    ]):
                                strength += 1
                            orders.remove(support_order)

        for convoy_order in convoy_orders_with_conflicts:

            # Determine the result. First, we need the maximum strength in this
            # contest. Then, we need to determine if more than one unit has
            # that strength. if so, it's a standoff.
            max_unit = max(units_in_convoy_terr,
                           key=units_in_convoy_terr.get)
            max_strength = units_in_convoy_terr[max_unit]
            standoff = False
            for unit, strength in units_in_convoy_terr.items():
                if strength == max_strength and unit is not max_unit:
                    standoff = True
            # CASE 1: Defender wins. Attackers are shifted back to their origin
            # territories and the convoy continues.
            if standoff or max_unit is convoy_order.unit:
                for unit in units_in_convoy_terr:
                    if unit is not convoy_order.unit:
                        units_in_convoy_terr.pop(unit)
                        if unit.territory not in locations:
                            locations[unit.territory] = {unit: 1}
                        else:
                            locations[unit.territory][unit] = 1
                            conflicts.add(unit.territory)
            # CASE 2: Attacker wins. The convoy is displaced and the convoyed
            # unit has to look for alternate routes. If none are found, the
            # convoyed unit remains in their original territory.

            # TODO: rework this section, once you have a list of routes from
            # the front end

            # else:
            #     displaced_units.append(units_in_convoy_terr.pop(
            #                            convoy_order.unit))
            #     for unit in units_in_convoy_terr:
            #         if unit is not max_unit:
            #             units_in_convoy_terr.pop(unit)
            #             if unit.territory not in locations:
            #                 locations[unit.territory] = {unit: 1}
            #             else:
            #                 locations[unit.territory][unit] = 1
            #                 conflicts.add(unit.territory)

        # Now in the second iteration, we determine supports.
        for order in orders:
            if order.order_type == 'support':
                # Check to make sure the supported action is actually being
                # performed.
                if (not locations.get(order.aux_destination) or
                        order.aux_unit not in
                        locations[order.aux_destination]):
                    continue
                # Check to make sure support isn't being cut
                if order.destination not in locations:
                    locations[order.destination] = {order.unit: 1}
                    locations[order.aux_destination][order.aux_unit] += 1
                else:
                    locations[order.destination][order.unit] = 1
                    conflicts.add(order.destination)
        pdb.set_trace()

    def delete(self, request, pk, format=None):
        pass
