from game import models


def process_retreat_turn(params):
    """
    The primary 'master' function which dictates how retreat turns
    should be processed.
    :param params: a dict with the following keys:
        'game': the Game object,
        'request_data': the data received from the frontend, with two
        sub-keys, 'orders' and 'convoy_routes',
        'retreat_phase_necessary': a boolean, which defaults to False.
    :return: None.
    """
    orders = [create_retreat_order_from_data(data, params['game'])
              for data in params['request_data']['orders'].values()]
    create_missing_delete_orders(params['game'], orders)
    locations = handle_retreat_conflicts(orders)
    update_retreat_unit_locations(locations, orders)


def create_retreat_order_from_data(data, objects):
    """
    Transforms the dictionary data for an order received from the
    frontend into an actual Order object.
    :param data: a dict with the object's data.
    :param objects: a dict with Game, Territory, and Unit objects.
    :return: a newly created Order object.
    """
    order = None
    if data['order_type'] == 'move':
        order = models.Order.objects.create(
            turn=objects['game'].current_turn(),
            unit=objects['units'][data['unit_id']],
            order_type='move',
            origin=objects['territories'][data['origin']],
            destination=objects['territories'][data['destination']],
            coast=data['coast'],
        )

    elif data['order_type'] == 'delete':
        unit = objects['units'][data['unit_id']]
        unit.deactivate()
        order = models.Order.objects.create(
            turn=objects['game'].current_turn(),
            unit=unit,
            order_type='delete',
            origin=objects['territories'][data['territory']]
        )

    return order


def create_missing_delete_orders(game, orders):
    game_units = set(game.units.filter(territory=None, active=True))
    for order in orders:
        game_units.discard(order.unit)
    for unit in game_units:
        models.Order.objects.create(
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
