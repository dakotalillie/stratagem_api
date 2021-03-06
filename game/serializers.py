from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
from authentication.models import Player
from .models import Game, Turn, Country, Territory, Unit


class UserLowDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Player
        fields = ('id',)


class CountryOverviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = ('id', 'user', 'name')


class GameOverviewSerializer(serializers.ModelSerializer):

    countries = CountryOverviewSerializer(many=True)
    current_turn = serializers.SerializerMethodField()

    def get_current_turn(self, obj):
        return TurnSerializer(obj.current_turn()).data

    class Meta:
        model = Game
        fields = ('id', 'title', 'countries', 'current_turn')


class TerritorySerializer(serializers.ModelSerializer):

    owner = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Territory
        fields = ('id', 'name', 'abbreviation', 'owner')


class UnitSerializer(serializers.ModelSerializer):

    territory = serializers.StringRelatedField(read_only=True)
    retreating_from = serializers.StringRelatedField(read_only=True)
    invaded_from = serializers.StringRelatedField(read_only=True)
    country = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Unit
        fields = ('id', 'unit_type', 'coast', 'territory', 'country',
                  'retreating_from', 'invaded_from')


class CountrySerializer(serializers.ModelSerializer):

    user = serializers.SerializerMethodField()
    territories = TerritorySerializer(many=True, read_only=True)
    units = serializers.SerializerMethodField()
    retreating_units = serializers.SerializerMethodField()

    def get_user(self, obj):
        return str(obj.user)

    def get_units(self, obj):
        if len(obj.units.all()) > 0:
            units = obj.units.filter(active=True, retreating_from=None)
            return UnitSerializer(units, many=True, read_only=True).data
        return []

    def get_retreating_units(self, obj):
        if len(obj.units.all()) > 0:
            units = obj.units.filter(active=True, territory=None)
            return UnitSerializer(units, many=True, read_only=True).data
        return []

    class Meta:
        model = Country
        fields = ('id', 'user', 'name', 'territories', 'units',
                  'retreating_units', 'ready', 'active')


class TurnSerializer(serializers.ModelSerializer):

    class Meta:
        model = Turn
        fields = ('season', 'year', 'phase', 'created_at')


class GameDetailSerializer(serializers.ModelSerializer):

    countries = CountrySerializer(many=True)
    current_turn = serializers.SerializerMethodField()

    def get_current_turn(self, obj):
        return TurnSerializer(obj.current_turn()).data

    class Meta:
        model = Game
        fields = ('id', 'title', 'countries', 'current_turn')
