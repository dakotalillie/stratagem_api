from game.lib.conflicts.Conflict import Conflict
from game.lib.conflicts.ConvoyRouteConflict import ConvoyRouteConflict
from game.lib.errors import RouteCannotYetBeResolved
from game.lib.ObjectsFromDatabase import ObjectsFromDatabase
from .TurnHandler import TurnHandler

import pdb


class DiplomaticTurnHandler(TurnHandler):

    """ PUBLIC METHODS """

    def __init__(self, game, request_data):
        super().__init__(game, request_data)
        self.orders = []
        self.convoy_routes = []
        self.locations = {}
        self.supports = []
        self.conflicts = set()
        self.displaced_units = []

    def process_turn(self):
        self._create_orders()
        self._create_convoy_routes()
        self._map_orders_to_locations_supports_and_conflicts()
        self._resolve_convoy_routes()
        self._add_supports()
        self._check_for_illegal_swaps()
        self._resolve_conflicts()
        self._update_unit_locations()

    """ PRIMARY HELPERS """

    def _create_orders(self):
        for order_data in self.request_data['orders'].values():
            self.orders.append(self._create_order_from_data(order_data))
        self._generate_missing_hold_orders()

    def _create_convoy_routes(self):
        for route_data in self.request_data['convoy_routes']:
            self.convoy_routes.append(self._map_convoy_route(route_data))

    def _map_orders_to_locations_supports_and_conflicts(self):
        for order in self.orders:
            if order.destination not in self.locations:
                self.locations[order.destination] = {order.unit: 1}
            else:
                self.locations[order.destination][order.unit] = 1
                self.conflicts.add(order.destination)
            if order.order_type == 'support':
                self.supports.append(order)

    def _resolve_convoy_routes(self):
        while len(self.convoy_routes) > 0:
            convoy_route = self.convoy_routes.pop(0)
            try:
                self._resolve_conflicts_in_convoy_route(convoy_route)
            except RouteCannotYetBeResolved:
                self.convoy_routes.append(convoy_route)

    def _add_supports(self):
        for support_order in self.supports:
            if not self._supported_unit_in_correct_location(support_order):
                continue
            if ((support_order.origin not in self.conflicts) or
                    self._support_would_be_cut_by_own_unit(support_order)):
                territory = support_order.aux_destination
                unit = support_order.aux_unit
                self.locations[territory][unit] += 1

    def _check_for_illegal_swaps(self):
        mapped_orders = {order.origin: order for order in self.orders}
        for order in mapped_orders.values():
            other_order = mapped_orders.get(order.destination)
            if order == other_order:
                continue
            if other_order and other_order.destination == order.origin:
                self._handle_illegal_swap(order, other_order)

    def _resolve_conflicts(self):
        while len(self.conflicts) > 0:
            conflict = Conflict(self, territory=self.conflicts.pop())
            conflict.resolve()

    def _update_unit_locations(self):
        self._update_displaced_units()
        self._reset_unit_territories()
        self._map_new_unit_locations()

    """ SECONDARY HELPERS """

    def _generate_missing_hold_orders(self):
        units_without_orders = self._identify_units_without_orders()
        for unit in units_without_orders:
            self.orders.append(self._create_default_hold_order(unit))

    def _identify_units_without_orders(self):
        units = set(self.db_objects.units.values())
        for order in self.orders:
            units.remove(order.unit)
        return units

    def _map_convoy_route(self, route_data):
        return {
            'unit': self.db_objects.units[route_data['unit_id']],
            'origin': self.db_objects.territories[route_data['origin']],
            'destination': self.db_objects.territories[
                route_data['destination']
            ],
            'route': [self.db_objects.units[unit['id']]
                      for unit in route_data['route']]
        }

    def _resolve_conflicts_in_convoy_route(self, convoy_route):
        convoy_broken = False
        for convoyer in convoy_route['route']:
            if convoyer.territory in self.conflicts:
                conflict = ConvoyRouteConflict(self, convoy_route, convoyer)
                conflict.resolve()
                if conflict.winner != convoyer:
                    convoy_broken = True
        if not convoy_broken:
            self.supports = [order for order in self.supports
                             if order.origin != convoy_route['destination']]

    def _supported_unit_in_correct_location(self, support_order):
        units_in_aux_destination = self.locations.get(
            support_order.aux_destination
        )
        if not units_in_aux_destination:
            return False
        return support_order.aux_unit in units_in_aux_destination

    def _support_would_be_cut_by_own_unit(self, support_order):
        for unit in self.locations[support_order.origin]:
            if unit.country != support_order.unit.country:
                return False
        return True

    def _handle_illegal_swap(self, order1, order2):
        unit1_in_dest = order1.unit in self.locations[order1.destination]
        unit2_in_dest = order2.unit in self.locations[order2.destination]
        if ((unit1_in_dest and unit2_in_dest) and not
                (order1.via_convoy or order2.via_convoy)):
            unit1_strength = self.locations[order1.destination][order1.unit]
            unit2_strength = self.locations[order2.destination][order2.unit]
            if unit1_strength >= unit2_strength:
                self.locations[order2.destination].pop(order2.unit)
                self._return_unit_to_origin(order2.unit)
            if unit1_strength <= unit2_strength:
                self.locations[order1.destination].pop(order1.unit)
                self._return_unit_to_origin(order1.unit)

    def _return_unit_to_origin(self, unit):
        if unit.territory not in self.locations:
            self.locations[unit.territory] = {unit: 1}
        else:
            self.locations[unit.territory][unit] = 1
            self.conflicts.add(unit.territory)

    def _update_displaced_units(self):
        for unit in self.displaced_units:
            unit.retreating_from = unit.territory
            unit.territory = None
            unit.save()

    def _reset_unit_territories(self):
        """
        Avoids issues with one-to-one fields in model. Topographical
        sort is not possible due to potential cycles.
        """
        for unit_dict in self.locations.values():
            if len(unit_dict):
                unit = list(unit_dict.keys())[0]
                unit.territory = None
                unit.save()

    def _map_new_unit_locations(self):
        orders_mapped_by_unit = {order.unit: order for order in self.orders}
        for territory, unit_dict in self.locations.items():
            if len(unit_dict):
                unit = list(unit_dict.keys())[0]
                order = orders_mapped_by_unit[unit]
                unit.territory = territory
                unit.coast = (order.coast if
                              order.destination == territory else
                              unit.coast)
                unit.save()
