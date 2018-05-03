import pdb
import json
from game.models import Game, Country, Territory, Unit, Turn, Order


def process_reinforcement_turn(game, request_data):
    for territory, order_data in request.data['orders'].items():
        utils.create_reinforcement_order_from_data(order_data, game)


def create_reinforcement_order_from_data(data, game):
    if data['order_type'] == 'create':
        territory = game.territories.get(abbreviation=data['territory'])
        country = game.countries.get(name=data['country'])
        unit = Unit.objects.create(
            territory=territory,
            unit_type=data['unit_type'],
            country=country,
            game=game,
            coast=data['coast']
        )

        Order.objects.create(
            turn=game.current_turn(),
            unit=unit,
            order_type='create',
            origin=territory,
            coast=data['coast']
        )

    elif data['order_type'] == 'delete':
        territory = game.territories.get(abbreviation=data['territory'])
        unit = Unit.objects.get(pk=data['unit_id'])
        unit.active = False
        unit.territory = None
        unit.save()

        Order.objects.create(
            turn=game.current_turn(),
            unit=unit,
            order_type='delete',
            origin=territory
        )