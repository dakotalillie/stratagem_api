from game import models


def process_retreat_turn(objects, request_data):
    """
    The primary 'master' function which dictates how retreat turns
    should be processed.
    :param objects: a dict containing objects from the ORM.
    :param request_data: the data received from the frontend, with two
           sub-keys, 'orders' and 'convoy_routes'.
    :return: None.
    """
    orders = [create_retreat_order_from_data(data, objects)
              for data in request_data['orders'].values()]
    create_missing_delete_orders(orders, objects)
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


def create_missing_delete_orders(orders, objects):
    """
    Creates delete orders for all of the game's units which are both
    active and displaced and which weren't explicitly given orders by
    the player(s).
    :param orders: a list of Order objects.
    :param objects: a dict with Game, Territory, and Unit objects.
    :return: None. Modifies orders.
    """
    game_units = set(objects['game'].units.filter(territory=None, active=True))
    for order in orders:
        game_units.discard(order.unit)
    for unit in game_units:
        orders.append(models.Order.objects.create(
            turn=objects['game'].current_turn(),
            unit=unit,
            order_type='delete',
            origin=unit.retreating_from
        ))
        unit.deactivate()


def handle_retreat_conflicts(orders):
    """
    Checks for situations where two or more units are retreating to the
    same territory. In these cases, all involved units are deactivated.
    :param orders: a list of Order objects
    :return: a dict of the Units' new locations.
    """
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
            unit.deactivate()
        locations.pop(conflict_location)
    return locations


def update_retreat_unit_locations(locations, orders):
    """
    Remaps locations of Unit objects.
    :param locations: a dict of territories and their occupying units.
    :param orders: a list of Order objects.
    :return: None.
    """
    mapped_orders = {order.unit: order for order in orders}
    for territory, unit_list in locations.items():
        unit = unit_list[0]
        unit.territory = territory
        unit.coast = mapped_orders[unit].coast
        unit.retreating_from = None
        unit.invaded_from = None
        unit.save()
