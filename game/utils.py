import pdb
import json
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
    aux_order_type = ''
    aux_origin = None
    aux_destination = None
    via_convoy = False

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

    if 'via_convoy' in data:
        via_convoy = data['via_convoy']

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
        aux_destination=aux_destination,
        via_convoy=via_convoy
    )

    order.save()

    return order


def create_reinforcement_order_from_data(data, game):
    if data['order_type'] == 'create':
        territory = game.territories.get(abbreviation=data['territory'])
        country = game.countries.get(name=data['country'])
        unit = Unit.objects.create(
            territory=territory,
            unit_type=data['unit_type'],
            country=country,
            game=game,
            coast=data['coast']
        )

        Order.objects.create(
            turn=game.current_turn(),
            unit=unit,
            order_type='create',
            origin=territory,
            coast=data['coast']
        )

    elif data['order_type'] == 'delete':
        territory = game.territories.get(abbreviation=data['territory'])
        unit = Unit.objects.get(pk=data['unit_id'])
        unit.active = False
        unit.territory = None
        unit.save()

        Order.objects.create(
            turn=game.current_turn(),
            unit=unit,
            order_type='delete',
            origin=territory
        )


def create_retreat_order_from_data(data, game):
    if data['order_type'] == 'move':
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

        order = Order.objects.create(
            turn=game.current_turn(),
            unit=Unit.objects.get(pk=data['unit_id']),
            order_type='move',
            origin=origin,
            destination=destination,
            coast=data['coast'],
        )

    elif data['order_type'] == 'delete':
        territory = game.territories.get(abbreviation=data['territory'])
        unit = Unit.objects.get(pk=data['unit_id'])
        unit.active = False
        unit.retreating_from = None
        unit.invaded_from = None
        unit.save()

        order = Order.objects.create(
            turn=game.current_turn(),
            unit=unit,
            order_type='delete',
            origin=territory
        )

    return order


def create_missing_hold_orders(game, orders):
    game_units = set(game.units.filter(active=True))
    for order in orders:
        game_units.remove(order.unit)
    for unit in game_units:
        order = Order.objects.create(
            turn=game.current_turn(),
            unit=unit,
            order_type='hold',
            origin=unit.territory,
            destination=unit.territory,
            coast=unit.coast
        )
        orders.append(order)


def create_missing_delete_orders(game, orders):
    game_units = set(game.units.filter(territory=None, active=True))
    for order in orders:
        game_units.discard(order.unit)
    for unit in game_units:
        Order.objects.create(
            turn=game.current_turn(),
            unit=unit,
            order_type='delete',
            origin=unit.retreating_from
        )

        unit.active = False
        unit.retreating_from = None
        unit.invaded_from = None
        unit.save()


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
    if count > 0:
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


def handle_retreat_conflicts(orders):
    locations = {}
    conflicts = set([])
    for order in orders:
        if order.destination not in locations:
            locations[order.destination] = [order.unit]
        # CASE: other unit(s) attempting to occupy territory
        else:
            locations[order.destination].append(order.unit)
            conflicts.add(order.destination)
    for conflict_location in conflicts:
        for unit in locations[conflict_location]:
            unit.active = False
            unit.retreating_from = None
            unit.invaded_from = None
            unit.save()
        locations.pop(conflict_location)

    return locations


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
            if (set(locations[support_order.origin].keys()) == set([
                support_order.unit,
                convoy_route['unit']
            ])):
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
    winner = determine_conflict_outcome(defender, units_in_terr, locations,
                                        conflicts)
    return_defeated_units_to_origins(conflict_location, units_in_terr, winner,
                                     locations, conflicts, displaced_units)


def determine_conflict_outcome(defender, units_in_terr, locations, conflicts):
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
            if (unit.territory == conflict_location):
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


def update_unit_locations(locations, displaced_units, orders):
    # Handle displaced units.
    for unit in displaced_units:
        unit.retreating_from = unit.territory
        unit.territory = None
        unit.save()
    # Map units' territories to their new locations.
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


def update_retreat_unit_locations(locations, orders):
    for territory, unit_list in locations.items():
        # Since at this point the unit dictionary will have only one
        # entry, the run time of this is not as bad as it looks.
        unit = unit_list[0]
        coast = unit.coast
        for order in orders:
            if order.unit == unit and order.destination == territory:
                coast = order.coast
                break
            elif order.unit == unit:
                break
        unit.territory = territory
        unit.coast = coast
        unit.retreating_from = None
        unit.invaded_from = None
        unit.save()


def create_new_turn(current_turn, retreat_phase_necessary):
    if current_turn.phase == 'diplomatic':
        if retreat_phase_necessary:
            turn = Turn(year=current_turn.year, season=current_turn.season,
                        phase='retreat', game=current_turn.game)
        elif not retreat_phase_necessary and current_turn.season == 'fall':
            turn = Turn(year=current_turn.year, season='fall',
                        phase='reinforcement', game=current_turn.game)
        else:
            turn = Turn(year=current_turn.year, season='fall',
                        phase='diplomatic', game=current_turn.game)
    elif current_turn.phase == 'retreat':
        if current_turn.season == 'fall':
            turn = Turn(year=current_turn.year, season='fall',
                        phase='reinforcement', game=current_turn.game)
        else:
            turn = Turn(year=current_turn.year, season='fall',
                        phase='diplomatic', game=current_turn.game)
    elif current_turn.phase == 'reinforcement':
        turn = Turn(year=current_turn.year + 1, season='spring',
                    phase='diplomatic', game=current_turn.game)
    turn.save()
    return turn


def update_territory_owners(game):
    with open('game/data/territories.json') as territories_json:
        territory_data = json.loads(territories_json.read())

    for unit in game.units.filter(active=True):
        water_terr = territory_data[
            unit.territory.abbreviation
        ]['type'] == 'water'
        if unit.country != unit.territory.owner and not water_terr:
            unit.territory.owner = unit.country
            unit.territory.save()
