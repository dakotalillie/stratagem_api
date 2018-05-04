import json


def update_turn(params):
    """
    Handles the creation of a new turn, once processing of the current
    turn has been completed.
    :param params: a dict with the following keys:
        'game': the Game object,
        'request_data': the data received from the frontend, with two
        sub-keys, 'orders' and 'convoy_routes',
        'retreat_phase_necessary': a boolean, which defaults to False.
    :return: None.
    """
    game = params['game']
    create_new_turn(game, game.current_turn(),
                    params['retreat_phase_necessary'])
    if game.current_turn().phase == 'reinforcement':
        update_territory_owners(game)


def create_new_turn(game, current_turn, retreat_phase_necessary):
    """
    Creates a new turn according to the previous turn and whether or
    not a retreat phase is necessary.
    :param game: a Game object.
    :param current_turn: the Game's most recently created Turn object.
    :param retreat_phase_necessary: a boolean.
    :return: a newly created Turn object.
    """
    turn = None
    if current_turn.phase == 'diplomatic':
        if retreat_phase_necessary:
            turn = game.turns.create(year=current_turn.year,
                                     season=current_turn.season,
                                     phase='retreat')
        elif not retreat_phase_necessary and current_turn.season == 'fall':
            turn = game.turns.create(year=current_turn.year, season='fall',
                                     phase='reinforcement')
        else:
            turn = game.turns.create(year=current_turn.year, season='fall',
                                     phase='diplomatic')
    elif current_turn.phase == 'retreat':
        if current_turn.season == 'fall':
            turn = game.turns.create(year=current_turn.year, season='fall',
                                     phase='reinforcement')
        else:
            turn = game.turns.create(year=current_turn.year, season='fall',
                                     phase='diplomatic')
    elif current_turn.phase == 'reinforcement':
        turn = game.turns.create(year=current_turn.year + 1, season='spring',
                                 phase='diplomatic')
    return turn


def update_territory_owners(game):
    """
    Iterates through the Game's units, and updates the ownership of the
    territories they occupy if necessary.
    :param game: a Game object.
    :return: none.
    """
    with open('game/data/territories.json') as territories_json:
        t_data = json.loads(territories_json.read())

    for unit in game.units.filter(active=True):
        water_terr = t_data[unit.territory.abbreviation]['type'] == 'water'
        if unit.country != unit.territory.owner and not water_terr:
            unit.territory.owner = unit.country
            unit.territory.save()
