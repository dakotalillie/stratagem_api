import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from . import constants
import json


class Player(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.first_name + " " + self.last_name


class Game(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    players = models.ManyToManyField(Player, through='Country',
                                     related_name='games')
    title = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Necessary to resolve unresolved references in PyCharm
    objects = models.Manager()
    territories = models.Manager()
    units = models.Manager()
    countries = models.Manager()
    turns = models.Manager()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # This code will trigger only when the game is first created. It
        # instantiates the turn/countries/territories/units for the
        # game.
        if len(self.countries.all()) == 0:
            country_players = kwargs.pop('country_players', {})
            countries = {c: Country(name=c, game=self,
                         user=country_players.get(c))
                         for c in constants.COUNTRY_NAMES}
            turn = Turn(year=1901, season='spring', phase='diplomatic',
                        game=self)

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
                                     owner=countries[country], game=self)
                    territories[terr_abbr] = terr
                for unit_dict in data['startingUnits']:
                    unit = Unit(unit_type=unit_dict['type'],
                                country=countries[country],
                                territory=territories[unit_dict['territory']],
                                coast=unit_dict['coast'], game=self)
                    units[unit.territory.abbreviation] = unit

            for terr_abbr, terr_data in territories_data.items():
                if terr_abbr not in territories:
                    terr = Territory(
                        name=terr_data['name'], abbreviation=terr_abbr,
                        game=self)
                    territories[terr_abbr] = terr

            super(Game, self).save(args, kwargs)
            turn.save()
            for country in countries.values():
                country.save()
            for territory in territories.values():
                territory.save()
            for unit in units.values():
                unit.save()

    def current_turn(self):
        return self.turns.latest('created_at')


class Country(models.Model):
    COUNTRIES = (
        ('Austria', 'Austria'),
        ('England', 'England'),
        ('France', 'France'),
        ('Germany', 'Germany'),
        ('Italy', 'Italy'),
        ('Russia', 'Russia'),
        ('Turkey', 'Turkey'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=7, choices=COUNTRIES)
    game = models.ForeignKey(Game, on_delete=models.CASCADE,
                             related_name='countries')
    user = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True,
                             blank=True, related_name='countries')

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
    # Necessary to avoid unresolved references in PyCharm.
    objects = models.Manager()

    def __str__(self):
        return self.abbreviation

    class Meta:
        verbose_name_plural = "territories"


class Unit(models.Model):
    UNIT_TYPES = (
        ('army', 'army'),
        ('fleet', 'fleet')
    )
    COASTS = (
        ('NC', 'north'),
        ('EC', 'east'),
        ('SC', 'south')
    )
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
    unit_type = models.CharField(max_length=5, choices=UNIT_TYPES)
    country = models.ForeignKey(Country, on_delete=models.CASCADE,
                                related_name='units')
    game = models.ForeignKey(Game, on_delete=models.CASCADE,
                             related_name='units')
    coast = models.CharField(max_length=2, choices=COASTS, blank=True)
    # Necessary to avoid unresolved references in PyCharm.
    objects = models.Manager()

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
    SEASONS = (
        ('spring', 'spring'),
        ('fall', 'fall'),
    )
    PHASES = (
        ('diplomatic', 'diplomatic'),
        ('retreat', 'retreat'),
        ('reinforcement', 'reinforcement')
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    year = models.PositiveSmallIntegerField(default=1901)
    season = models.CharField(max_length=6, choices=SEASONS)
    phase = models.CharField(max_length=13, choices=PHASES)
    game = models.ForeignKey(Game, on_delete=models.CASCADE,
                             related_name='turns')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s %s %s" % (self.phase, self.season, self.year)


class Order(models.Model):
    ORDER_TYPES = (
        ('hold', 'hold'),
        ('move', 'move'),
        ('support', 'support'),
        ('convoy', 'convoy'),
        ('create', 'create')
    )
    AUX_ORDER_TYPES = (
        ('hold', 'hold'),
        ('move', 'move')
    )
    COASTS = (
        ('NC', 'north'),
        ('EC', 'east'),
        ('SC', 'south')
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    turn = models.ForeignKey(Turn, on_delete=models.CASCADE,
                             related_name='orders')
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE,
                             related_name='orders')
    order_type = models.CharField(max_length=7, choices=ORDER_TYPES)
    origin = models.ForeignKey(Territory, on_delete=models.CASCADE,
                               related_name='+')
    destination = models.ForeignKey(Territory, on_delete=models.CASCADE,
                                    blank=True, null=True, related_name='+')
    coast = models.CharField(max_length=2, choices=COASTS, blank=True)
    aux_unit = models.ForeignKey(Unit, on_delete=models.CASCADE, blank=True,
                                 null=True, related_name='+', )
    aux_order_type = models.CharField(max_length=4, choices=AUX_ORDER_TYPES,
                                      blank=True)
    aux_origin = models.ForeignKey(Territory, on_delete=models.CASCADE,
                                   blank=True, null=True,
                                   related_name='+')
    aux_destination = models.ForeignKey(Territory, on_delete=models.CASCADE,
                                        blank=True, null=True,
                                        related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)
    via_convoy = models.BooleanField(default=False)
    # Necessary to avoid unresolved references in PyCharm.
    objects = models.Manager()
