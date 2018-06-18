from game.models import Order


def create_order_from_data(order_data, db_objects):
    aux_unit = None
    aux_order_type = ''
    aux_origin = None
    aux_destination = None
    via_convoy = False

    if 'aux_unit_id' in order_data:
        aux_unit = db_objects.units[order_data['aux_unit_id']]
        aux_order_type = order_data['aux_order_type']
        aux_origin = db_objects.territories[order_data['aux_origin']]
        aux_destination = db_objects.territories[
            order_data['aux_destination']
        ]

    if 'via_convoy' in order_data:
        via_convoy = order_data['via_convoy']

    order = models.Order(
        turn=db_objects.game.current_turn(),
        unit=db_objects.units[order_data['unit_id']],
        order_type=order_data['order_type'],
        origin=db_objects.territories[order_data['origin']],
        destination=db_objects.territories[order_data['destination']],
        coast=order_data['coast'],
        aux_unit=aux_unit,
        aux_order_type=aux_order_type,
        aux_origin=aux_origin,
        aux_destination=aux_destination,
        via_convoy=via_convoy
    )

    order.save()
    return order


def create_default_hold_order(unit):
    order = models.Order(
                turn=self.db_objects.game.current_turn(),
                unit=unit,
                order_type='hold',
                origin=unit.territory,
                destination=unit.territory,
                coast=unit.coast
            )

    order.save()
    return order
