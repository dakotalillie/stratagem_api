from .Conflict import Conflict


class ConvoyRouteConflict(Conflict):

    def __init__(self, turn_handler, convoy_route, convoyer):
        super().__init__(turn_handler, territory=convoyer.territory)
        self.convoy_route = convoy_route
        self.convoyer = convoyer

    def resolve(self):
        self._determine_winner()
        if self.winner == self.convoyer:
            self._return_defeated_units_to_origins()
            self.turn_handler.conflicts.remove(self.territory)
        else:
            self._return_defeated_units_to_origins()
            if not self._more_possible_convoy_routes():
                locations[convoy_route['destination']].pop(unit)
                return_unit_to_origin(unit=convoy_route['unit'])
                # Check if there are other ways destination
                # territory is being attacked. If not, remove
                # the destination from conflicts
                more_attacks = len(locations[
                    convoy_route['destination']
                ].keys()) > 1
                if not more_attacks:
                    conflicts.remove(convoy_route['destination'])
            # Since the convoy route is broken, we can consider it
            # resolved without checking the other units
            conflicts.remove(convoyer.territory)
            return True        

    def _determine_winner(self):
        for unit in self.units_in_combat:
            self._add_supports(unit)
        return super()._determine_winner(defender=self.convoyer)

    def _add_supports(self, unit):
        unit_supports = [
            order for order in self.turn_handler.supports
            if order.aux_unit == unit
        ]
        for support_order in unit_supports:
            cut = self._check_if_support_is_cut(support_order)
            if not cut:
                self.units_in_combat[unit] += 1
                self.turn_handler.supports.remove(support_order)

    def _check_if_support_is_cut(self, support_order):
        if self._support_can_only_be_cut_by_convoyed_unit(support_order):
            if self._more_possible_convoy_routes():
                raise RouteCannotBeResolved
            else:
                return False
        if support_order.origin in self.turn_handler.conflicts:
            return True
        return False

    def _support_can_only_be_cut_by_convoyed_unit(self, support_order):
        units_in_support_origin = set(
            self.turn_handler.locations[support_order.origin].keys()
        )
        return (
            units_in_support_origin ==
            {support_order.unit, self.convoy_route['unit']}
        )

    def _more_possible_convoy_routes(self):
        for cr in self.turn_handler.convoy_routes:
            if (cr['origin'] == self.convoy_route['origin'] and
                    cr['destination'] == self.convoy_route['destination']):
                return True
        return False
