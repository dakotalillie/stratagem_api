from game.lib.ObjectsFromDatabase import ObjectsFromDatabase
from game.lib.errors import RouteCannotBeResolved, ConvoyerDisplaced
from game.utils import create_order_from_data
from .TurnHandler import TurnHandler
from .ConvoyRouteConflict import ConvoyRouteConflict

class DiplomaticTurnHandler(TurnHandler):

    def __init__(self, game, request_data):
        super().__init__(game, request_data)
        self.orders = []
        self.convoy_routes = []
        self.locations = {}
        self.supports = []
        self.conflicts = set([])
        self.displaced_units = []

    def process_turn(self):
        self._create_orders()
        self._create_convoy_routes()
        self._map_orders_to_locations_supports_and_conflicts()
        self._resolve_convoy_routes()
        add_supports(locations, supports, conflicts)
        check_for_illegal_swaps(orders, locations, conflicts)
        while len(conflicts) > 0:
            conflict_location = conflicts.pop()
            resolve_conflict(conflict_location, locations, conflicts,
                            displaced_units)

        update_unit_locations(locations, displaced_units, orders)
        return len(displaced_units) > 0

    def _create_orders(self):
        for order_data in self.request_data['orders'].values():
            self.orders.append(self._create_order_from_data(order_data))
        self._generate_missing_hold_orders()

    def _generate_missing_hold_orders(self):
        units_without_orders = _identify_units_without_orders()
        for unit in units_without_orders:
            order = models.Order.objects.create(
                turn=self.db_objects.game.current_turn(),
                unit=unit,
                order_type='hold',
                origin=unit.territory,
                destination=unit.territory,
                coast=unit.coast
            )
            self.orders.append(order)

    def _identify_units_without_orders(self):
        units = set(self.db_objects.units.values())
        for order in self.orders:
            units.remove(order.unit)
        return units

    def _create_convoy_routes(self):
        for route_data in self.request_data['convoy_routes']:
            self.convoy_routes.append(_map_convoy_route(route_data))

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
            resolved = _resolve_conflicts_in_convoy_route(convoy_route)
            if not resolved:
                self.convoy_routes.append(convoy_route)

    def _resolve_conflicts_in_convoy_route(self, convoy_route):
        for convoyer in convoy_route['route']:
            if convoyer.territory in self.conflicts:
                try:
                    ConvoyRouteConflict(self, convoy_route, convoyer).resolve()
                except ConvoyerDisplaced:
                    return True
                except RouteCannotBeResolved:
                    return False
        # Convoy was successful. Remove supports from destination if necessary.
        new_supports = [order for order in supports
                        if order.origin != convoy_route['destination']]
        supports[:] = new_supports
        return True

    def check_for_illegal_swaps(orders, locations, conflicts):
        mapped_orders = {order.origin: order for order in orders}
        for order in mapped_orders.values():
            d_order = mapped_orders.get(order.destination)
            if d_order and d_order.destination == order.origin:
                unit_in_location = order.unit in locations[order.destination]
                d_unit_in_location = d_order.unit in locations[d_order.destination]
                # Check if matter hasn't already resolved
                if ((unit_in_location and d_unit_in_location) and not
                        (order.via_convoy or d_order.via_convoy)):
                    unit_strength = locations[order.destination][order.unit]
                    match_strength = locations[d_order.destination][d_order.unit]
                    if unit_strength >= match_strength:
                        locations[d_order.destination].pop(d_order.unit)
                        return_unit_to_origin(d_order.unit, locations, conflicts)
                    if unit_strength <= match_strength:
                        locations[order.destination].pop(order.unit)
                        return_unit_to_origin(order.unit, locations, conflicts)

    def update_unit_locations(locations, displaced_units, orders):
        # Handle displaced units.
        for unit in displaced_units:
            unit.retreating_from = unit.territory
            unit.territory = None
            unit.save()
        # Set unit territories to None, to avoid issues with one-to-one
        # field in the model. Would be nice to do topological sort to avoid
        # too many database calls, but unfortunately the graph of moves may
        # be cyclic
        for unit_dict in locations.values():
            unit = list(unit_dict.keys())[0]
            unit.territory = None
            unit.save()
        # Then, map units' territories to their new locations.
        orders_mapped_by_unit = {order.unit: order for order in orders}
        for territory, unit_dict in locations.items():
            unit = list(unit_dict.keys())[0]
            coast = unit.coast
            order = orders_mapped_by_unit[unit]
            if order.destination == territory:
                coast = order.coast
            unit.territory = territory
            unit.coast = coast
            unit.save()
