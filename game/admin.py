from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Player, Game, Country, Unit, Territory, Turn, Order


class CountryInline(admin.TabularInline):
    model = Country
    extra = 7


class GameAdmin(admin.ModelAdmin):
    inlines = [CountryInline]


admin.site.register(Game, GameAdmin)
admin.site.register(Player, UserAdmin)
