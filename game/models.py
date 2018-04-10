import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Player(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class Game(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    players = models.ManyToManyField(Player, through='Country',
                                     related_name='games')
    title = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

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
    active = models.BooleanField(default=True)
    unit_type = models.CharField(max_length=5, choices=UNIT_TYPES)
    country = models.ForeignKey(Country, on_delete=models.CASCADE,
                                related_name='units')
    game = models.ForeignKey(Game, on_delete=models.CASCADE,
                             related_name='units')
    coast = models.CharField(max_length=2, choices=COASTS, blank=True)

    def __str__(self):
        return "%s %s %s" % (self.country, self.unit_type, self.territory)


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
    aux_order_type = models.CharField(max_length=4, choices=AUX_ORDER_TYPES)
    aux_origin = models.ForeignKey(Territory, on_delete=models.CASCADE,
                                   blank=True, null=True,
                                   related_name='+')
    aux_destination = models.ForeignKey(Territory, on_delete=models.CASCADE,
                                        blank=True, null=True,
                                        related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)
