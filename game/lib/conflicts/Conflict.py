class Conflict():

    def __init__(self, turn_handler, territory):
        self.turn_handler = turn_handler
        self.territory = territory
        self.units = turn_handler.locations[territory]
        self.winner = None

    def add_supports(locations, supports, conflicts):
        for order in supports:
            # Check to make sure the supported action is actually being
            # performed.
            if (not locations.get(order.aux_destination) or
                    order.aux_unit not in locations[order.aux_destination]):
                continue
            # Check to make sure support isn't being cut
            if order.origin not in conflicts:
                locations[order.aux_destination][order.aux_unit] += 1

    def resolve_conflict():
        units_in_terr = locations[conflict_location]
        defender = None
        for unit in units_in_terr:
            if unit.territory == conflict_location:
                defender = unit
                break
        winner = determine_conflict_outcome(defender, units_in_terr)
        return_defeated_units_to_origins()

    def _determine_winner(defender):
        max_unit = max(self.units, key=self.units.get)
        max_strength = self.units[max_unit]
        standoff = False
        for unit, strength in self.units.items():
            if strength == max_strength and unit != max_unit:
                standoff = True
        if standoff:
            self.winner = defender if defender
        else:
            self.winner = max_unit

    def _return_defeated_units_to_origins(self):
        units_to_move = [unit for unit in self.units if unit != self.winner]
        for unit in units_to_move:
            if not self._losing_unit_belongs_to_winner(unit):
                self.units.pop(unit)
                if not self._unit_will_be_displaced(unit):
                    self._return_unit_to_origin(unit)

    def _losing_unit_belongs_to_winner(self, unit):
        if (unit.territory == self.territory and
                unit.country == self.winner.country):
            self.units.pop(winner)
            self._return_unit_to_origin(winner)
            return True

    def _unit_will_be_displaced(self, unit):
        if unit.territory == self.territory:
            unit.invaded_from = self.winner.territory
            self.turn_handler.displaced_units.append(unit)

    def _return_unit_to_origin(self, unit):
        if unit.territory not in self.turn_handler.locations:
            self.turn_handler.locations[unit.territory] = {unit: 1}
        else:
            self.turn_handler.locations[unit.territory][unit] = 1
            self.turn_handler.conflicts.add(unit.territory)
