from .TurnProcessor import TurnProcessor


class ReinforcementTurnProcessor(TurnProcessor):

    def process_turn(self):
        self._create_orders()
        self._process_orders()
        self._update_turn()
        self._reset_country_ready_states()

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
            territory=order.origin,
            unit_type=order.unit_type,
            country=order.country,
            coast=order.coast
        )

    def _deactivate_unit(self, order):
        order.unit.deactivate()

    def _update_turn(self):
        current_turn = self.game.current_turn()
        self.game.turns.create(
            year=current_turn.year + 1,
            season='spring',
            phase='diplomatic'
        )
