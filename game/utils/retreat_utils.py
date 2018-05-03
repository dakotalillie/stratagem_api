import pdb
import json
from game.models import Game, Country, Territory, Unit, Turn, Order


def process_retreat_turn(game, request_data):
    orders = [utils.create_retreat_order_from_data(data, game)
              for unit_id, data in request_data['orders'].items()]
    utils.create_missing_delete_orders(game, orders)
    locations = utils.handle_retreat_conflicts(orders)
    utils.update_retreat_unit_locations(locations, orders)


def create_retreat_order_from_data(data, game):
    if data['order_type'] == 'move':
        unit = Unit.objects.get(pk=data['unit_id'])
        game = unit.game
        origin = Territory.objects.get(
            game=game,
            abbreviation=data['origin']
        )
        destination = Territory.objects.get(
            game=game,
            abbreviation=data['destination']
        )

        order = Order.objects.create(
            turn=game.current_turn(),
            unit=Unit.objects.get(pk=data['unit_id']),
            order_type='move',
            origin=origin,
            destination=destination,
            coast=data['coast'],
        )

    elif data['order_type'] == 'delete':
        territory = game.territories.get(abbreviation=data['territory'])
        unit = Unit.objects.get(pk=data['unit_id'])
        unit.active = False
        unit.retreating_from = None
        unit.invaded_from = None
        unit.save()

        order = Order.objects.create(
            turn=game.current_turn(),
            unit=unit,
            order_type='delete',
            origin=territory
        )

    return order


def create_missing_delete_orders(game, orders):
    game_units = set(game.units.filter(territory=None, active=True))
    for order in orders:
        game_units.discard(order.unit)
    for unit in game_units:
        Order.objects.create(
            turn=game.current_turn(),
            unit=unit,
            order_type='delete',
            origin=unit.retreating_from
        )

        unit.active = False
        unit.retreating_from = None
        unit.invaded_from = None
        unit.save()


def handle_retreat_conflicts(orders):
    locations = {}
    conflicts = set([])
    for order in orders:
        if order.destination not in locations:
            locations[order.destination] = [order.unit]
        # CASE: other unit(s) attempting to occupy territory
        else:
            locations[order.destination].append(order.unit)
            conflicts.add(order.destination)
    for conflict_location in conflicts:
        for unit in locations[conflict_location]:
            unit.active = False
            unit.retreating_from = None
            unit.invaded_from = None
            unit.save()
        locations.pop(conflict_location)

    return locations


def update_retreat_unit_locations(locations, orders):
    for territory, unit_list in locations.items():
        # Since at this point the unit dictionary will have only one
        # entry, the run time of this is not as bad as it looks.
        unit = unit_list[0]
        coast = unit.coast
        for order in orders:
            if order.unit == unit and order.destination == territory:
                coast = order.coast
                break
            elif order.unit == unit:
                break
        unit.territory = territory
        unit.coast = coast
        unit.retreating_from = None
        unit.invaded_from = None
        unit.save()
