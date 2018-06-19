from game.lib.turn_processors.DiplomaticTurnProcessor import \
                                                      DiplomaticTurnProcessor
from game.lib.turn_processors.RetreatTurnProcessor import RetreatTurnProcessor


def get_turn_processor(game, data):
    phase = game.current_turn().phase
    if phase == 'diplomatic':
        return DiplomaticTurnProcessor(game, data)
    elif phase == 'retreat':
        return RetreatTurnProcessor(game, data)
    elif phase == 'reinforcement':
        pass


def dict_keys_to_snake_case(old_dict):
    new_dict = {}
    for key, value in old_dict.items():
        new_key = camel_case_to_snake_case(key)
        if type(value) == dict:
            new_dict[new_key] = dict_keys_to_snake_case(value)
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
