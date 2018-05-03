from game import models


def process_diplomatic_turn(params):
    """
    This is the primary 'master' function which dictates how diplomatic
    turns should be processed.
    :param params: a dict with the following keys:
        'game': the Game object,
        'request_data': the data received from the frontend, with two
        sub-keys, 'orders' and 'convoy_routes',
        'retreat_phase_necessary': a boolean, which defaults to False.
    :return: None.
    """
    objects = {
        'game': params['game'],
        'units': {u.id: u for u in params['game'].units.filter(active=True)},
        'territories': {t.abbreviation: t for t in
                        params['game'].territories.all()}
    }
    orders = [create_order_from_data(data, objects)
              for unit_id, data in params['request_data']['orders'].items()]
    create_missing_hold_orders(game, orders)
    convoy_routes = [map_convoy_route_to_models(game, route)
                     for route in params['request_data']['convoy_routes']]
    locations, supports, conflicts = map_orders_to_locations(orders)
    displaced_units = []
    # Convoy routes need to be resolved first, because if there's a unit
    # providing support in the territory that the convoyed unit is
    # moving to, that support could be cut.
    while len(convoy_routes) > 0:
        convoy_route = convoy_routes.pop(0)
        other_routes = more_possible_convoy_routes(convoy_routes,
                                                   convoy_route)
        resolved = resolve_conflicts_in_convoy_route(
            convoy_route, locations, supports, conflicts, displaced_units,
            other_routes
        )
        if not resolved:
            convoy_routes.append(convoy_route)
    add_supports(locations, supports, conflicts)
    check_for_illegal_swaps(orders, locations, conflicts)
    while len(conflicts) > 0:
        conflict_location = conflicts.pop()
        resolve_conflict(conflict_location, locations, conflicts,
                         displaced_units)

    update_unit_locations(locations, displaced_units, orders)
    params['retreat_phase_necessary'] = len(displaced_units) > 0


def create_order_from_data(data, objects):
    """
    This function transforms the dictionary data for an order received
    from the frontend into an actual Order object.
    :param data: a dict with the object's data.
    :param objects: a dict with the following shape:
        'game': a Game object,
        'units: a dict with the game's units, mapped by id
        'territories': a dict with the game's territories, mapped by
                       abbreviation
    :return: a newly created Order object.
    """
    aux_unit = None
    aux_order_type = ''
    aux_origin = None
    aux_destination = None
    via_convoy = False

    if 'aux_unit_id' in data:
        aux_unit = objects['units'][data['aux_unit_id']]
        aux_order_type = data['aux_order_type']
        aux_origin = objects['territories'][data['aux_origin']]
        aux_destination = objects['territories'][data['aux_destination']]

    if 'via_convoy' in data:
        via_convoy = data['via_convoy']

    order = models.Order(
        turn=objects['game'].current_turn(),
        unit=objects['units'][data['unit_id']],
        order_type=data['order_type'],
        origin=objects['territories'][data['origin']],
        destination=objects['territories'][data['destination']],
        coast=data['coast'],
        aux_unit=aux_unit,
        aux_order_type=aux_order_type,
        aux_origin=aux_origin,
        aux_destination=aux_destination,
        via_convoy=via_convoy
    )

    order.save()

    return order


def create_missing_hold_orders(game, orders):
    """
    This function creates hold orders for all of the game's active units
    which weren't explicitly given orders by the player(s).
    :param game: a Game object.
    :param orders: a list of Order objects.
    :return: None. Simply modifies orders.
    """
    game_units = set(game.units.filter(active=True))
    for order in orders:
        game_units.remove(order.unit)
    for unit in game_units:
        order = models.Order.objects.create(
            turn=game.current_turn(),
            unit=unit,
            order_type='hold',
            origin=unit.territory,
            destination=unit.territory,
            coast=unit.coast
        )
        orders.append(order)


def map_convoy_route_to_models(game, data):
    mapped_data = {'unit': models.Unit.objects.get(pk=data['unit_id']),
                   'origin': game.territories.get(abbreviation=data['origin']),
                   'destination': game.territories.get(
                       abbreviation=data['destination']),
                   'route': [models.Unit.objects.get(pk=unit['id'])
                             for unit in data['route']]}
    return mapped_data


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


def more_possible_convoy_routes(convoy_routes, route):
    count = len([cr for cr in convoy_routes
                 if cr['origin'] == route['origin'] and
                 cr['destination'] == route['destination']])
    if count > 0:
        return True
    return False


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
                conflicts.remove(defender.territory)
                return True
            elif outcome == 'defer':
                return False
    # Convoy was successful. Remove supports from destination if necessary.
    new_supports = [order for order in supports
                    if order.origin != convoy_route['destination']]
    supports[:] = new_supports
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
            # This checks whether the only way support could be cut in
            # the territory the convoyed unit is moving to is by the
            # convoyed unit itself.
            if (set(locations[support_order.origin].keys()) == {
                  support_order.unit, convoy_route['unit']}):
                # Check if there are other routes with the same
                # origin and destination. If so, defer, and
                # sort those out first. Otherwise, with no other routes,
                # the convoyed until cannot cut support from the
                # territory is is moving to.
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
    # TODO: potentially refactor this into determine_conflict_outcome
    max_unit = max(units_in_terr, key=units_in_terr.get)
    max_strength = units_in_terr[max_unit]
    standoff = False
    for unit, strength in units_in_terr.items():
        if strength == max_strength and unit != max_unit:
            standoff = True
    if standoff or max_unit == defender:
        return 'defender wins', defender
    else:
        return 'defender loses', max_unit


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


def check_for_illegal_swaps(orders, locations, conflicts):
    for order in orders:
        # TODO: Find a more efficient way to do this.
        match = None
        for other_order in orders:
            if (other_order.destination == order.origin and
                    order.destination == other_order.origin and
                    order.id != other_order.id):
                match = other_order
        if match:
            unit_in_location = order.unit in locations[order.destination]
            match_in_location = (match.unit in locations[match.destination])
            # Check if matter hasn't already resolved
            if ((unit_in_location and match_in_location) and not
                    (order.via_convoy or match.via_convoy)):
                unit_strength = locations[order.destination][order.unit]
                match_strength = locations[match.destination][match.unit]
                if unit_strength >= match_strength:
                    locations[match.destination].pop(match.unit)
                    return_unit_to_origin(match.unit, locations, conflicts)
                if unit_strength <= match_strength:
                    locations[order.destination].pop(order.unit)
                    return_unit_to_origin(order.unit, locations, conflicts)


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


def update_unit_locations(locations, displaced_units, orders):
    # Handle displaced units.
    for unit in displaced_units:
        unit.retreating_from = unit.territory
        unit.territory = None
        unit.save()
    # First, set all unit territories to None so they can be freshly
    # remapped. Maybe would be better to do topological sort?
    for territory, unit_dict in locations.items():
        for unit in unit_dict:
            unit.territory = None
            unit.save()
    # Then, map units' territories to their new locations.
    for territory, unit_dict in locations.items():
        # Since at this point the unit dictionary will have only one
        # entry, the run time of this is not as bad as it looks.
        for unit in unit_dict:
            # TODO: this is a temporary fix. restructure data later.
            coast = unit.coast
            for order in orders:
                if order.unit == unit and order.destination == territory:
                    coast = order.coast
                    break
                elif order.unit == unit:
                    break
            unit.territory = territory
            unit.coast = coast
            unit.save()
