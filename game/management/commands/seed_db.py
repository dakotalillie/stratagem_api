import json

from django.core.management.base import BaseCommand
from game.models import Player, Game, Country, Unit, Territory, Turn
from .utils import seed_scenarios


class Command(BaseCommand):

    help = 'Seeds the database'

    def _create_player(self):
        player = Player(
            username='bewguy101',
            email='bewguy101@gmail.com',
            first_name='Dakota',
            last_name='Lillie',
        )
        player.set_password('helloworld')
        player.save()

    def _create_game(self):
        Game.objects.create(title='Demo Game')

    def _create_turn(self):
        game = Game.objects.first()
        Turn.objects.create(
            year=1901,
            season='spring',
            phase='diplomatic',
            game=game
        )

    def _create_countries(self, country_data):
        game = Game.objects.first()
        player = Player.objects.first()

        for country in country_data:
            Country.objects.create(name=country, game=game, user=player)

    def _create_territories(self, country_data, territory_data):
        game = Game.objects.first()

        created_territories = {}

        for country_name, data in country_data.items():
            country = Country.objects.get(name=country_name, game=game)
            for terr_abbr in data['startingTerritories']:
                Territory.objects.create(
                    name=territory_data[terr_abbr]['name'],
                    abbreviation=terr_abbr,
                    owner=country,
                    game=game
                )
                created_territories[terr_abbr] = True

        for terr_abbr, terr_data in territory_data.items():
            if terr_abbr not in created_territories:
                Territory.objects.create(
                    name=terr_data['name'],
                    abbreviation=terr_abbr,
                    game=game
                )

    def _create_units(self, country_data):
        game = Game.objects.first()
        seed_scenarios.test_unit_deletion(game)

    def handle(self, *args, **options):
        with open('game/data/countries.json') as countries_json:
            country_data = json.loads(countries_json.read())

        with open('game/data/territories.json') as territories_json:
            territory_data = json.loads(territories_json.read())

        self._create_player()
        self._create_game()
        self._create_turn()
        self._create_countries(country_data)
        self._create_territories(country_data, territory_data)
        self._create_units(country_data)
