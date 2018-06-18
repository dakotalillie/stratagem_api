from abc import ABC

from game.lib.ObjectsFromDatabase import ObjectsFromDatabase


class TurnHandler(ABC):

    def __init__(self, game, request_data):
        self.request_data = request_data
        self.db_objects = ObjectsFromDatabase(game)
        self.retreat_phase_necessary = False
