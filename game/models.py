import uuid
from django.db import models
from django.contrib.auth.models import User


class Game(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=50)


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
    game = models.ForeignKey('Game', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                             blank=True)


class Territory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=30)
    abbreviation = models.CharField(max_length=3)
    owner = models.ForeignKey('Country', on_delete=models.CASCADE, null=True,
                              blank=True)
    unit = models.OneToOneField('Unit', on_delete=models.SET_NULL, null=True,
                                blank=True)


class Unit(models.Model):
    UNIT_TYPES = (
        ('A', 'army'),
        ('F', 'fleet')
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    active = models.BooleanField(default=True)
    unitType = models.CharField(max_length=1, choices=UNIT_TYPES)
    country = models.ForeignKey('Country', on_delete=models.CASCADE)


class Turn(models.Model):
    SEASONS = (
        ('S', 'spring'),
        ('F', 'fall'),
    )
    PHASES = (
        ('diplomatic', 'diplomatic'),
        ('retreat', 'retreat'),
        ('reinforcement', 'reinforcement')
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    year = models.PositiveSmallIntegerField(default=1901)
    season = models.CharField(max_length=1, choices=SEASONS)
    phase = models.CharField(max_length=15, choices=PHASES)
    game = models.ForeignKey('Game', on_delete=models.CASCADE)


class Order(models.Model):
    ORDER_TYPES = (
        ('hold', 'hold'),
        ('move', 'move'),
        ('support', 'support'),
        ('convoy', 'convoy'),
        ('disband', 'disband'),
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
    turn = models.ForeignKey('Turn', on_delete=models.CASCADE)
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE)
    order_type = models.CharField(max_length=7, choices=ORDER_TYPES)
    destination = models.ForeignKey('Territory', on_delete=models.CASCADE,
                                    blank=True, null=True)
    coast = models.CharField(max_length=2, choices=COASTS, blank=True)
    aux_unit = models.ForeignKey('Unit', on_delete=models.CASCADE, blank=True,
                                 null=True, related_name='+', )
    aux_order_type = models.CharField(max_length=4, choices=AUX_ORDER_TYPES)
    aux_destination = models.ForeignKey('Territory', on_delete=models.CASCADE,
                                        blank=True, null=True,
                                        related_name='+')
