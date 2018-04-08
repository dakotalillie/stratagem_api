from django.db import models


class Game(models.Model):
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
    name = models.CharField(max_length=7, choices=COUNTRIES)
