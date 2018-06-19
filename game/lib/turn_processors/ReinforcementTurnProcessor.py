from .TurnProcessor import TurnProcessor


class ReinforcementTurnProcessor(TurnProcessor):

    def __init__(self, game, request_data):
        super().__init__(game, request_data)

    def process_turn(self):
        self._create_orders()
        self._process_orders()

    def _create_orders(self):
        for order_data in self.request_data['orders'].values():
            self.orders.append(self._create_order_from_data(order_data))

    def _process_orders(self):
        for order in self.orders:
            if order.order_type == 'create':
                self._create_unit(order)
            elif order.order_type == 'delete':
                self._deactivate_unit(order)

    def _create_unit(self, order):
        self.game.units.create(
            territory=order.origin
            unit_type=order.unit_type
        )


def create_reinforcement_order_from_data(data, objects):

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
