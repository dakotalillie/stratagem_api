from django.contrib import admin
from .models import Game, Country, Unit, Territory, Turn, Order


class CountryInline(admin.TabularInline):
    model = Country
    extra = 7


class GameAdmin(admin.ModelAdmin):
    inlines = [CountryInline]


admin.site.register(Game, GameAdmin)
