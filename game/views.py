from django.http import Http404
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from . import models
from . import serializers
from .utils import diplomatic_utils
from .utils import reinforcement_utils
from .utils import retreat_utils
from .utils import update_turn_utils
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

    def post(self, request):
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

    def post(self, request):
        country_players = {country: request.user for country in
                           constants.COUNTRY_NAMES}
        game = models.Game(title='New Sandbox')
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

    def post(self, request, pk):
        params = {
            'game':                    models.Game.objects.get(pk=pk),
            'request_data':            request.data,
            'retreat_phase_necessary': False
        }
        if params['game'].current_turn().phase == 'diplomatic':
            diplomatic_utils.process_diplomatic_turn(params)
        elif params['game'].current_turn().phase == 'retreat':
            retreat_utils.process_retreat_turn(params)
        elif params['game'].current_turn().phase == 'reinforcement':
            reinforcement_utils.process_reinforcement_turn(params)
        update_turn_utils.update_turn(params)
        serializer = serializers.GameDetailSerializer(params['game'])
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk, format=None):
        pass
