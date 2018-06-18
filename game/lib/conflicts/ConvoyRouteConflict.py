from .Conflict import Conflict

import pdb


class ConvoyRouteConflict(Conflict):

    def __init__(self, turn_handler, convoy_route, convoyer):
        super().__init__(turn_handler, territory=convoyer.territory)
        self.convoy_route = convoy_route
        self.convoyer = convoyer

    def resolve(self):
        self._determine_winner()
        self._return_defeated_units_to_origins()
        self.turn_handler.conflicts.remove(self.territory)
        if not self._more_possible_convoy_routes():
            self._return_convoyed_unit_to_origin()
            self._check_if_convoy_destination_can_be_removed_from_conflicts()

    def _determine_winner(self):
        for unit in self.units:
            self._add_supports_for_unit(unit)
        return super()._determine_winner(defender=self.convoyer)

    def _add_supports_for_unit(self, unit):
        unit_supports = [
            order for order in self.turn_handler.supports
            if order.aux_unit == unit
        ]
        for support_order in unit_supports:
            cut = self._check_if_support_is_cut(support_order)
            if not cut:
                supported_unit = support_order.aux_unit
                self.units[supported_unit] += 1
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

    def _return_convoyed_unit_to_origin(self):
        convoyed_unit = self.convoy_route['unit']
        self.turn_handler.locations[
            self.convoy_route['destination']
        ].pop(convoyed_unit)
        self.turn_handler._return_unit_to_origin(convoyed_unit)

    def _check_if_convoy_destination_can_be_removed_from_conflicts(self):
        convoy_destination = self.convoy_route['destination']
        convoy_destination_still_being_attacked = (
            len(self.turn_handler.locations[convoy_destination].keys()) > 1
        )
        if not convoy_destination_still_being_attacked:
            self.turn_handler.conflicts.remove(convoy_destination)
