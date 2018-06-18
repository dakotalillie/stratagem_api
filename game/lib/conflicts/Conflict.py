class Conflict():

    def __init__(self, turn_handler, territory):
        self.turn_handler = turn_handler
        self.territory = territory
        self.units = turn_handler.locations[territory]
        self.winner = None

    def resolve(self):
        defender = next((unit for unit in self.units
                         if unit.territory == self.territory),
                        None)
        self._determine_winner(defender)
        self._return_defeated_units_to_origins()

    def _determine_winner(self, defender):
        max_unit = max(self.units, key=self.units.get)
        max_strength = self.units[max_unit]
        standoff = False
        for unit, strength in self.units.items():
            if strength == max_strength and unit != max_unit:
                standoff = True
        if standoff:
            self.winner = defender if defender else None
        else:
            self.winner = max_unit

    def _return_defeated_units_to_origins(self):
        units_to_move = [unit for unit in self.units if unit != self.winner]
        for unit in units_to_move:
            if not self._losing_unit_belongs_to_winner(unit):
                self.units.pop(unit)
                if not self._unit_will_be_displaced(unit):
                    self.turn_handler._return_unit_to_origin(unit)

    def _losing_unit_belongs_to_winner(self, unit):
        if (unit.territory == self.territory and
                unit.country == self.winner.country):
            self.units.pop(winner)
            self.turn_handler._return_unit_to_origin(winner)
            return True

    def _unit_will_be_displaced(self, unit):
        if unit.territory == self.territory:
            unit.invaded_from = self.winner.territory
            self.turn_handler.displaced_units.append(unit)
            self.turn_handler.retreat_phase_necessary = True
