class Conflict():

    def __init__(self):
        pass

    def return_defeated_units_to_origins(conflict_location, units_in_terr, winner,
                                     locations, conflicts, displaced_units):
    units_to_move = [unit for unit in units_in_terr if unit != winner]

    for unit in units_to_move:
        # Cannot displace own unit.
        if (unit.territory == conflict_location and unit.country ==
                winner.country):
            units_in_terr.pop(winner)
            return_unit_to_origin(winner, locations, conflicts)
        else:
            units_in_terr.pop(unit)
            if unit.territory == conflict_location:
                unit.invaded_from = winner.territory
                displaced_units.append(unit)
            else:
                return_unit_to_origin(unit, locations, conflicts)


    def return_unit_to_origin(unit, locations, conflicts):
        if unit.territory not in locations:
            locations[unit.territory] = {unit: 1}
        else:
            locations[unit.territory][unit] = 1
            conflicts.add(unit.territory)


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


    def resolve_conflict(conflict_location, locations, conflicts, displaced_units):
        units_in_terr = locations[conflict_location]
        defender = None
        for unit in units_in_terr:
            if unit.territory == conflict_location:
                defender = unit
                break
        winner = determine_conflict_outcome(defender, units_in_terr)
        return_defeated_units_to_origins(conflict_location, units_in_terr, winner,
                                        locations, conflicts, displaced_units)


    def determine_conflict_outcome(defender, units_in_terr):
        max_unit = max(units_in_terr, key=units_in_terr.get)
        max_strength = units_in_terr[max_unit]
        standoff = False
        for unit, strength in units_in_terr.items():
            if strength == max_strength and unit != max_unit:
                standoff = True
        if standoff:
            return defender if defender else None
        else:
            return max_unit