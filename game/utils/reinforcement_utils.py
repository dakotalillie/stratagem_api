from game import models


def process_reinforcement_turn(objects, request_data):
    """
    The primary 'master' function which dictates how reinforcement turns
    should be processed.
    :param objects: a dict containing objects from the ORM.
    :param request_data: the data received from the frontend, with two
           sub-keys, 'orders' and 'convoy_routes'.
    :return: None.
    """
    for order_data in request_data['orders'].values():
        create_reinforcement_order_from_data(order_data, objects)


def create_reinforcement_order_from_data(data, objects):
    """
    Transforms the dictionary data for an order received from the
    frontend into an actual Order object.
    :param data: a dict with the object's data.
    :param objects: a dict with Game, Territory, and Unit objects.
    :return: a newly created Order object.
    """
    if data['order_type'] == 'create':
        territory = objects['territories'][data['origin']]
        country = objects['countries'][data['country']]
        unit = objects['game'].units.create(
            territory=territory,
            unit_type=data['unit_type'],
            country=country,
            coast=data['coast']
        )

        return models.Order.objects.create(
            turn=objects['game'].current_turn(),
            unit=unit,
            order_type='create',
            origin=territory,
            coast=data['coast']
        )

    elif data['order_type'] == 'delete':
        territory = objects['territories'][data['origin']]
        unit = objects['units'][data['unit_id']]
        unit.deactivate()

        return models.Order.objects.create(
            turn=objects['game'].current_turn(),
            unit=unit,
            order_type='delete',
            origin=territory
        )