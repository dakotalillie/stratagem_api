from game.models import Game, Country, Territory, Unit, Turn, Order


def create_order_from_data(data):
    unit = Unit.objects.get(pk=data['unit_id'])
    game = unit.game
    origin = Territory.objects.get(
        game=game,
        abbreviation=data['origin']
    )
    destination = None
    aux_unit = None
    aux_order_type = None
    aux_origin = None
    aux_destination = None

    if 'destination' in data:
        destination = Territory.objects.get(
            game=game,
            abbreviation=data['destination']
        )
    if 'aux_unit' in data:
        aux_unit = Unit.objects.get(pk=data['aux_unit_id'])
        aux_order_type = data['aux_order_type']
        aux_origin = Territory.objects.get(
            game=game,
            abbreviation=data.get('aux_origin')
        )
    if 'aux_destination' in data:
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
