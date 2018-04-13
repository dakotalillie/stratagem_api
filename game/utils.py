import pdb
from game.models import Game, Country, Territory, Unit, Turn, Order


def create_order_from_data(data):
    unit = Unit.objects.get(pk=data['unit_id'])
    game = unit.game
    origin = Territory.objects.get(
        game=game,
        abbreviation=data['origin']
    )
    destination = Territory.objects.get(
        game=game,
        abbreviation=data['destination']
    )
    aux_unit = None
    aux_order_type = None
    aux_origin = None
    aux_destination = None

    if 'aux_unit_id' in data:
        aux_unit = Unit.objects.get(pk=data['aux_unit_id'])
        aux_order_type = data['aux_order_type']
        aux_origin = Territory.objects.get(
            game=game,
            abbreviation=data.get('aux_origin')
        )
        aux_destination = Territory.objects.get(
            game=game,
            abbreviation=data.get('aux_destination')
        )

    order = Order(
        turn=game.current_turn(),
        unit=Unit.objects.get(pk=data['unit_id']),
        order_type=data['order_type'],
        origin=origin,
        destination=destination,
        coast=data['coast'],
        aux_unit=aux_unit,
        aux_order_type=aux_order_type,
        aux_origin=aux_origin,
        aux_destination=aux_destination
    )

    return order


def map_convoy_route_to_models(data):
    mapped_data = {}
    mapped_data['unit'] = Unit.objects.get(pk=data['unit_id'])
    game = mapped_data['unit'].game
    mapped_data['origin'] = Territory.objects.get(
        game=game,
        abbreviation=data['origin']
    )
    mapped_data['destination'] = Territory.objects.get(
        game=game,
        abbreviation=data['destination']
    )
    mapped_data['route'] = [Unit.objects.get(pk=unit['id'])
                            for unit in data['route']]
    return mapped_data


def more_possible_convoy_routes(convoy_routes, route):
    count = len([cr for cr in convoy_routes
                 if cr['origin'] == route['origin'] and
                 cr['destination'] == route['destination']])
    if count > 1:
        return True
    return False


def map_orders_to_locations(orders):
    locations = {}
    supports = []
    conflicts = set([])
    for order in orders:
        # CASE: no moves recorded for this territory yet
        if order.destination not in locations:
            locations[order.destination] = {order.unit: 1}
        # CASE: other unit(s) attempting to occupy territory
        else:
            locations[order.destination][order.unit] = 1
            conflicts.add(order.destination)
        # Hold on to to supports, so we can factor them in later.
        if order.order_type == 'support':
            supports.append(order)
    return locations, supports, conflicts


def resolve_conflicts_in_convoy_route(convoy_route, locations,
                                      supports, conflicts, displaced_units,
                                      other_routes):
    for convoyeur in convoy_route['route']:
        if convoyeur.territory in conflicts:
            defender = convoyeur
            units_in_terr = locations[convoyeur.territory]
            outcome, winner = determine_convoy_conflict_outcome(
                convoy_route, defender, units_in_terr, locations, supports,
                conflicts, other_routes,
            )
            # CASE 1: Defender wins. Attackers are shifted back to
            # their original territories and the convoy continues.
            if outcome == 'defender wins':
                return_defeated_units_to_origins(
                    convoyeur.territory, units_in_terr, defender, locations,
                    conflicts, displaced_units
                )
                conflicts.remove(defender.territory)
            # CASE 2: Attacker wins. The convoy is displaced and the
            # convoyed unit has to look for alternate routes. If none
            # are found, the convoyed unit remains in their original
            # territory.
            elif outcome == 'defender loses':
                return_defeated_units_to_origins(
                    convoyeur.territory, units_in_terr, winner, locations,
                    conflicts, displaced_units
                )
                if not other_routes:
                    unit = convoy_route['unit']
                    locations[convoy_route['destination']].pop(unit)
                    return_unit_to_origin(unit, locations, conflicts)
                    # Check if there are other ways destination territory
                    # is being attacked. If not, remove the destination from
                    # conflicts
                    more_attacks = len(locations[
                        convoy_route['destination']
                    ].keys()) > 1
                    if not more_attacks:
                        conflicts.remove(convoy_route['destination'])

                # Since the convoy route is broken, we can consider it resolved
                # without checking the other units
                conflicts.remove(defender.territory)
                return True
            elif outcome == 'defer':
                return False
    return True


def determine_convoy_conflict_outcome(convoy_route, defender, units_in_terr,
                                      locations, supports, conflicts,
                                      other_routes):
    for unit in units_in_terr:
        # Find all supports for that unit.
        unit_supports = [
            order for order in supports
            if order.aux_unit == unit
        ]
        # Check to make sure supports haven't been cut.
        for support_order in unit_supports:
            # This checks whether the only way support could be cut in the
            # territory the convoyed unit is moving to is by the convoyed unit
            # itself.
            if (set(locations[support_order.origin].keys()) == set([
                support_order.unit,
                convoy_route['unit']
            ])):
                # Check if there are other routes with the same
                # origin and destination. If so, defer, and
                # sort those out first. Otherwise, with no other routes, the
                # convoyed until cannot cut support from the territory is is
                # moving to.
                if other_routes:
                    return 'defer', None
                else:
                    units_in_terr[unit] += 1
                    supports.remove(support_order)
            if support_order.origin not in conflicts:
                units_in_terr[unit] += 1
                supports.remove(support_order)
    # Determine the result. First, we need the maximum strength
    # in this contest. Then, we need to determine if more than
    # one unit has that strength. if so, it's a standoff.
    max_unit = max(units_in_terr, key=units_in_terr.get)
    max_strength = units_in_terr[max_unit]
    standoff = False
    for unit, strength in units_in_terr.items():
        if strength == max_strength and unit is not max_unit:
            standoff = True
    if standoff or max_unit is defender:
        return 'defender wins', defender
    else:
        return 'defender loses', max_unit


def add_supports(locations, supports):
    for order in supports:
        # Check to make sure the supported action is actually being performed.
        if (not locations.get(order.aux_destination) or
                order.aux_unit not in locations[order.aux_destination]):
            continue
        # Check to make sure support isn't being cut
        if order.origin not in conflicts:
            locations[order.aux_destination][order.aux_unit] += 1


def resolve_conflict(conflict_location, locations, conflicts, displaced_units):
    units_in_terr = locations[conflict_location]
    winner = determine_conflict_outcome(units_in_terr, locations, conflicts)
    return_defeated_units_to_origins(conflict_location, units_in_terr, winner,
                                     locations, conflicts, displaced_units)


def determine_conflict_outcome(units_in_terr, locations, conflicts):
    max_unit = max(units_in_terr, key=units_in_terr.get)
    max_strength = units_in_terr[max_unit]
    standoff = False
    for unit, strength in units_in_terr.items():
        if strength == max_strength and unit is not max_unit:
            standoff = True
    if standoff:
        return None
    else:
        return max_unit


def return_defeated_units_to_origins(conflict_location, units_in_terr, winner,
                                     locations, conflicts, displaced_units):
    units_to_move = [unit for unit in units_in_terr if unit is not winner]
    for unit in units_to_move:
        units_in_terr.pop(unit)
        if unit.territory == conflict_location:
            displaced_units.append(unit)
        else:
            return_unit_to_origin(unit, locations, conflicts)


def return_unit_to_origin(unit, locations, conflicts):
    if unit.territory not in locations:
        locations[unit.territory] = {unit: 1}
    else:
        locations[unit.territory][unit] = 1
        conflicts.add(unit.territory)
