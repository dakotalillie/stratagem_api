import json

from django.core.management.base import BaseCommand
from game.models import Player, Game, Country, Unit, Territory, Turn


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

        for country_name, data in country_data.items():
            country = Country.objects.get(name=country_name, game=game)
            for unit in data['startingUnits']:
                territory = Territory.objects.get(
                    abbreviation=unit['territory'],
                    game=game
                )
                Unit.objects.create(
                    unit_type=unit['type'],
                    country=country,
                    territory=territory,
                    coast=unit['coast'],
                    game=game
                )

    def _create_custom_units(self):
        game = Game.objects.first()

        france = Country.objects.get(name='France', game=game)
        italy = Country.objects.get(name='Italy', game=game)

        tun = Territory.objects.get(abbreviation='Tun', game=game)
        tys = Territory.objects.get(abbreviation='TYS', game=game)
        ion = Territory.objects.get(abbreviation='ION', game=game)
        rom = Territory.objects.get(abbreviation='Rom', game=game)
        nap = Territory.objects.get(abbreviation='Nap', game=game)
        apu = Territory.objects.get(abbreviation='Apu', game=game)

        Unit.objects.create(
            unit_type='army',
            country=france,
            territory=tun,
            game=game
        )
        Unit.objects.create(
            unit_type='fleet',
            country=france,
            territory=tys,
            game=game
        )
        Unit.objects.create(
            unit_type='fleet',
            country=france,
            territory=ion,
            game=game
        )
        Unit.objects.create(
            unit_type='army',
            country=france,
            territory=apu,
            game=game
        )
        Unit.objects.create(
            unit_type='fleet',
            country=italy,
            territory=nap,
            game=game
        )
        Unit.objects.create(
            unit_type='fleet',
            country=italy,
            territory=rom,
            game=game
        )

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
        # self._create_units(country_data)
        self._create_custom_units()
