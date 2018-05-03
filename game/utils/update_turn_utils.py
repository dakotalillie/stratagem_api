def update_turn(game, retreat_phase_necessary):
    create_new_turn(game.current_turn(), retreat_phase_necessary)
    if game.current_turn().phase == 'reinforcement':
        utils.update_territory_owners(game)


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
