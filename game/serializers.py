import pdb

from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
from .models import Player, Game, Turn, Country, Territory, Unit


class GameOverviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Game
        fields = ('id', 'title')


class UserSerializer(serializers.ModelSerializer):

    games = GameOverviewSerializer(many=True, read_only=True)

    class Meta:
        model = Player
        fields = ('id', 'username', 'email',
                  'first_name', 'last_name', 'games')


class UserSerializerWithToken(serializers.ModelSerializer):

    token = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True)
    games = GameOverviewSerializer(many=True, read_only=True)

    def get_token(self, obj):
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(obj)
        token = jwt_encode_handler(payload)
        return token

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    class Meta:
        model = Player
        fields = ('token', 'username', 'email', 'first_name',
                  'last_name', 'password', 'games')


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

    territories = TerritorySerializer(many=True, read_only=True)
    units = serializers.SerializerMethodField()
    retreating_units = serializers.SerializerMethodField()

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
                  'retreating_units')


class TurnSerializer(serializers.ModelSerializer):

    class Meta:
        model = Turn
        fields = ('season', 'year', 'phase')


class GameDetailSerializer(serializers.ModelSerializer):

    countries = CountrySerializer(many=True)
    current_turn = serializers.SerializerMethodField()

    def get_current_turn(self, obj):
        return TurnSerializer(obj.current_turn()).data

    class Meta:
        model = Game
        fields = ('id', 'title', 'countries', 'current_turn')
