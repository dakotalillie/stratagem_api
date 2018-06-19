from game.lib import ModelCompatibleEnum


class COUNTRIES(ModelCompatibleEnum):
    Austria = 'Austria'
    England = 'England'
    France = 'France'
    Germany = 'Germany'
    Italy = 'Italy'
    Russia = 'Russia'
    Turkey = 'Turkey'


class UNIT_TYPES(ModelCompatibleEnum):
    army = 'army'
    fleet = 'fleet'


class COASTS(ModelCompatibleEnum):
    NC = 'NC'
    EC = 'EC'
    SC = 'SC'


class SEASONS(ModelCompatibleEnum):
    spring = 'spring'
    fall = 'fall'


class PHASES(ModelCompatibleEnum):
    diplomatic = 'diplomatic'
    retreat = 'retreat'
    reinforcement = 'reinforcement'


class ORDER_TYPES(ModelCompatibleEnum):
    hold = 'hold'
    move = 'move'
    support = 'support'
    convoy = 'convoy'
    create = 'create'
    delete = 'delete'


class AUX_ORDER_TYPES(ModelCompatibleEnum):
    hold = 'hold'
    move = 'move'
