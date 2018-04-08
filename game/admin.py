from django.contrib import admin
from .models import Game, Country, Unit, Territory, Turn, Order


class GameAdmin(admin.ModelAdmin):
    pass


admin.site.register(Game)
