from rest_framework import serializers
from .models import Player, Game, Country, Territory, Unit


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


class TerritorySerializer(serializers.ModelSerializer):

    owner = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Territory
        fields = ('id', 'name', 'abbreviation', 'owner')


class UnitSerializer(serializers.ModelSerializer):

    territory = serializers.StringRelatedField(read_only=True)
    country = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Unit
        fields = ('id', 'unit_type', 'coast', 'territory', 'country')


class CountrySerializer(serializers.ModelSerializer):

    territories = TerritorySerializer(many=True, read_only=True)
    units = UnitSerializer(many=True, read_only=True)

    class Meta:
        model = Country
        fields = ('id', 'name', 'territories', 'units')


class GameDetailSerializer(serializers.ModelSerializer):

    countries = CountrySerializer(many=True)

    class Meta:
        model = Game
        fields = ('id', 'title', 'countries')
