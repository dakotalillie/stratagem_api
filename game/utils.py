from game.lib.turn_processors import DiplomaticTurnProcessor
from game.lib.turn_processors import RetreatTurnProcessor
from game.lib.turn_processors import ReinforcementTurnProcessor


def get_turn_processor(game, data):
    phase = game.current_turn().phase
    if phase == 'diplomatic':
        return DiplomaticTurnProcessor(game, data)
    elif phase == 'retreat':
        return RetreatTurnProcessor(game, data)
    elif phase == 'reinforcement':
        return ReinforcementTurnProcessor(game, data)


def dict_keys_to_snake_case(old_dict):
    new_dict = {}
    for key, value in old_dict.items():
        new_key = camel_case_to_snake_case(key)
        if type(value) == dict:
            new_dict[new_key] = dict_keys_to_snake_case(value)
        elif type(value) == list:
            new_dict[new_key] = [dict_keys_to_snake_case(i) for i in value]
        else:
            new_dict[new_key] = value
    return new_dict


def camel_case_to_snake_case(string):
    words = []
    last_slice = 0
    for index, character in enumerate(string):
        if character.istitle():
            word = string[last_slice:index]
            words.append(word.lower())
            last_slice = index
    last_word = string[last_slice:]
    words.append(last_word.lower())
    return '_'.join(words)
