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