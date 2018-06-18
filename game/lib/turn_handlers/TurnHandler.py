from abc import ABC

from game.models import Order
from game.lib.ObjectsFromDatabase import ObjectsFromDatabase

import pdb


class TurnHandler(ABC):

    def __init__(self, game, request_data):
        self.request_data = request_data
        self.db_objects = ObjectsFromDatabase(game)
        self.retreat_phase_necessary = False

    def _create_order_from_data(self, order_data):
        aux_unit = None
        aux_order_type = ''
        aux_origin = None
        aux_destination = None
        via_convoy = False

        if 'aux_unit_id' in order_data:
            aux_unit = self.db_objects.units[order_data['aux_unit_id']]
            aux_order_type = order_data['aux_order_type']
            aux_origin = self.db_objects.territories[order_data['aux_origin']]
            aux_destination = self.db_objects.territories[
                order_data['aux_destination']
            ]

        if 'via_convoy' in order_data:
            via_convoy = order_data['via_convoy']

        order = Order(
            turn=self.db_objects.game.current_turn(),
            unit=self.db_objects.units[order_data['unit_id']],
            order_type=order_data['order_type'],
            origin=self.db_objects.territories[order_data['origin']],
            destination=self.db_objects.territories[order_data['destination']],
            coast=order_data['coast'],
            aux_unit=aux_unit,
            aux_order_type=aux_order_type,
            aux_origin=aux_origin,
            aux_destination=aux_destination,
            via_convoy=via_convoy
        )

        order.save()
        return order

    def _create_default_hold_order(self, unit):
        order = Order(
                    turn=self.db_objects.game.current_turn(),
                    unit=unit,
                    order_type='hold',
                    origin=unit.territory,
                    destination=unit.territory,
                    coast=unit.coast
                )

        order.save()
        return order
