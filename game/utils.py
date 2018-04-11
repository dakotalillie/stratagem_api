import pdb
from game.models import Game, Country, Territory, Unit, Turn, Order


def create_order_from_data(data):
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
    aux_unit = None
    aux_order_type = None
    aux_origin = None
    aux_destination = None

    if 'aux_unit_id' in data:
        aux_unit = Unit.objects.get(pk=data['aux_unit_id'])
        aux_order_type = data['aux_order_type']
        aux_origin = Territory.objects.get(
            game=game,
            abbreviation=data.get('aux_origin')
        )
        aux_destination = Territory.objects.get(
            game=game,
            abbreviation=data.get('aux_destination')
        )

    order = Order(
        turn=game.current_turn(),
        unit=Unit.objects.get(pk=data['unit_id']),
        order_type=data['order_type'],
        origin=origin,
        destination=destination,
        coast=data['coast'],
        aux_unit=aux_unit,
        aux_order_type=aux_order_type,
        aux_origin=aux_origin,
        aux_destination=aux_destination
    )

    return order


def map_convoy_route_to_models(data):
    mapped_data = {}
    mapped_data['unit'] = Unit.objects.get(pk=data['unit_id'])
    game = mapped_data['unit'].game
    mapped_data['origin'] = Territory.objects.get(
        game=game,
        abbreviation=data['origin']
    )
    mapped_data['destination'] = Territory.objects.get(
        game=game,
        abbreviation=data['destination']
    )
    mapped_data['route'] = [Unit.objects.get(pk=unit['id'])
                            for unit in data['route']]
    return mapped_data


def more_possible_convoy_routes(convoy_routes, route):
    count = len([cr for cr in convoy_routes
                 if cr['origin'] == route['origin'] and
                 cr['destination'] == route['destination']])
    if count > 1:
        return True
    return False
