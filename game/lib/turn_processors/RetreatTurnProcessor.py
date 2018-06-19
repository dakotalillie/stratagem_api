from .TurnProcessor import TurnProcessor


class RetreatTurnProcessor(TurnProcessor):

    def __init__(self, game, request_data):
        super().__init__(game, request_data)
        self.locations = {}
        self.conflicts = set()

    def process_turn(self):
        self._create_orders()
        self._deactivate_deleted_units()
        self._map_orders_to_locations_and_conflicts()
        self._deactivate_units_in_conflicts()
        self._update_unit_locations()
        self._update_turn()
        if self.game.current_turn().phase == 'reinforcement':
            self._update_territory_owners()

    def _create_orders(self):
        for order_data in self.request_data['orders'].values():
            self.orders.append(self._create_order_from_data(order_data))
        self._generate_missing_delete_orders()

    def _generate_missing_delete_orders(self):
        displaced_units = self._identify_displaced_units_without_orders()
        for unit in displaced_units:
            self.orders.append(self._create_default_delete_order(unit))

    def _identify_displaced_units_without_orders(self):
        displaced_units = {unit for unit in self.db_objects.units.values()
                           if not unit.territory}
        for order in self.orders:
            displaced_units.remove(order.unit)
        return displaced_units

    def _deactivate_deleted_units(self):
        delete_orders = [order for order in self.orders
                         if order.order_type == 'delete']
        for order in delete_orders:
            order.unit.deactivate()

    def _map_orders_to_locations_and_conflicts(self):
        for order in self.orders:
            if order.destination not in self.locations:
                self.locations[order.destination] = [order.unit]
            else:
                self.locations[order.destination].append(order.unit)
                self.conflicts.add(order.destination)

    def _deactivate_units_in_conflicts(self):
        for conflict_location in self.conflicts:
            for unit in self.locations[conflict_location]:
                unit.deactivate()
            self.locations.pop(conflict_location)

    def _update_unit_locations(self):
        mapped_orders = {order.unit: order for order in self.orders}
        for territory, unit_list in self.locations.items():
            unit = unit_list[0]
            unit.territory = territory
            unit.coast = mapped_orders[unit].coast
            unit.retreating_from = None
            unit.invaded_from = None
            unit.save()

    def _update_turn(self):
        current_turn = self.game.current_turn()
        if current_turn.season == 'fall':
            self.game.turns.create(
                year=current_turn.year,
                season='fall',
                phase='reinforcement'
            )
        else:
            self.game.turns.create(
                year=current_turn.year,
                season='fall',
                phase='diplomatic'
            )