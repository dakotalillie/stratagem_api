import uuid
import json
from django.db import models
from authentication.models import Player
from game import constants


class Game(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    players = models.ManyToManyField(Player, through='Country',
                                     related_name='games')
    title = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        country_players = kwargs.pop('country_players', {})
        initialize_units = kwargs.pop('initialize_units', False)
        super(Game, self).save(args, kwargs)
        if len(self.countries.all()) == 0:
            self.initialize_game(country_players, initialize_units)

    def initialize_game(self, country_players, initialize_units):
        countries = {c: Country(name=c, game=self,
                     user=country_players.get(c))
                     for c in constants.COUNTRIES.as_list()}

        turn = Turn(year=1901, season='spring', phase='diplomatic',
                    game=self)

        with open('game/data/countries.json') as countries_json:
            country_data = json.loads(countries_json.read())

        with open('game/data/territories.json') as territories_json:
            territories_data = json.loads(territories_json.read())

        territories = {}
        for country, data in country_data.items():
            for terr_abbr in data['startingTerritories']:
                terr = Territory(name=territories_data[terr_abbr]['name'],
                                 abbreviation=terr_abbr,
                                 owner=countries[country], game=self)
                territories[terr_abbr] = terr

        for terr_abbr, terr_data in territories_data.items():
            if terr_abbr not in territories:
                terr = Territory(name=terr_data['name'],
                                 abbreviation=terr_abbr, game=self)
                territories[terr_abbr] = terr

        turn.save()
        for country in countries.values():
            country.save()
        for territory in territories.values():
            territory.save()

        if initialize_units:
            self.initialize_units(countries, territories)

    def initialize_units(self, countries, territories):
          
        with open('game/data/countries.json') as countries_json:
            country_data = json.loads(countries_json.read())

        for country, data in country_data.items():
            for unit_dict in data['startingUnits']:
                unit = Unit(unit_type=unit_dict['type'],
                            country=countries[country],
                            territory=territories[unit_dict['territory']],
                            coast=unit_dict['coast'], game=self)
                unit.save()

    def current_turn(self):
        return self.turns.latest('created_at')


class Country(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=7,
                            choices=constants.COUNTRIES.as_tuples())
    game = models.ForeignKey(Game, on_delete=models.CASCADE,
                             related_name='countries')
    user = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True,
                             blank=True, related_name='countries')
    ready = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "countries"


class Territory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=30)
    abbreviation = models.CharField(max_length=3)
    owner = models.ForeignKey(Country, on_delete=models.CASCADE, null=True,
                              blank=True, related_name='territories')
    game = models.ForeignKey(Game, on_delete=models.CASCADE,
                             related_name='territories')

    def __str__(self):
        return self.abbreviation

    class Meta:
        verbose_name_plural = "territories"


class Unit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    territory = models.OneToOneField(Territory, on_delete=models.CASCADE,
                                     blank=True, null=True)
    retreating_from = models.OneToOneField(Territory, on_delete=models.CASCADE,
                                           blank=True, null=True,
                                           related_name='retreating_unit')
    invaded_from = models.OneToOneField(Territory, on_delete=models.CASCADE,
                                        blank=True, null=True,
                                        related_name='+')
    active = models.BooleanField(default=True)
    unit_type = models.CharField(max_length=5,
                                 choices=constants.UNIT_TYPES.as_tuples())
    country = models.ForeignKey(Country, on_delete=models.CASCADE,
                                related_name='units')
    game = models.ForeignKey(Game, on_delete=models.CASCADE,
                             related_name='units')
    coast = models.CharField(max_length=2,
                             choices=constants.COASTS.as_tuples(), blank=True)

    def __str__(self):
        return "%s %s %s" % (self.country, self.unit_type, self.territory)

    def displace(self, invaded_from):
        self.retreating_from = self.territory
        self.invaded_from = invaded_from
        self.territory = None
        self.save()

    def deactivate(self):
        self.territory = None
        self.coast = ''
        self.retreating_from = None
        self.invaded_from = None
        self.active = False
        self.save()


class Turn(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    year = models.PositiveSmallIntegerField(default=1901)
    season = models.CharField(max_length=6,
                              choices=constants.SEASONS.as_tuples())
    phase = models.CharField(max_length=13,
                             choices=constants.PHASES.as_tuples())
    game = models.ForeignKey(Game, on_delete=models.CASCADE,
                             related_name='turns')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s %s %s" % (self.phase, self.season, self.year)


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    turn = models.ForeignKey(Turn, on_delete=models.CASCADE,
                             related_name='orders')
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE,
                             related_name='orders', blank=True, null=True)
    unit_type = models.CharField(max_length=5,
                                 choices=constants.UNIT_TYPES.as_tuples())
    country = models.ForeignKey(Country, on_delete=models.CASCADE,
                                related_name='orders')
    order_type = models.CharField(max_length=7,
                                  choices=constants.ORDER_TYPES.as_tuples())
    origin = models.ForeignKey(Territory, on_delete=models.CASCADE,
                               related_name='+')
    destination = models.ForeignKey(Territory, on_delete=models.CASCADE,
                                    blank=True, null=True, related_name='+')
    coast = models.CharField(max_length=2,
                             choices=constants.COASTS.as_tuples(), blank=True)
    aux_unit = models.ForeignKey(Unit, on_delete=models.CASCADE, blank=True,
                                 null=True, related_name='+', )
    aux_order_type = models.CharField(
        max_length=4,
        choices=constants.AUX_ORDER_TYPES.as_tuples(),
        blank=True
    )
    aux_origin = models.ForeignKey(Territory, on_delete=models.CASCADE,
                                   blank=True, null=True,
                                   related_name='+')
    aux_destination = models.ForeignKey(Territory, on_delete=models.CASCADE,
                                        blank=True, null=True,
                                        related_name='+')
    via_convoy = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
