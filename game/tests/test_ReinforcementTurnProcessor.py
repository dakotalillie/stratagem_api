from game.lib import StratagemTestCase
from game.lib.turn_processors import ReinforcementTurnProcessor


class CreateUnitTestCase(StratagemTestCase):

    def setUp(self):
        super().setUp()
        self.set_current_turn(1901, 'fall', 'reinforcement')
        self.create('Par', 'army', 'France')
        ReinforcementTurnProcessor(self.game, self.request_data).process_turn()

    def test_correctly_processes_turn(self):
        self.assertTerritoryHasUnit('Par')


class DeleteUnitTestCase(StratagemTestCase):

    def setUp(self):
        super().setUp()
        self.set_current_turn(1901, 'fall', 'reinforcement')
        self.par = self.create_unit('Par', 'army', 'France')
        self.delete(self.par)
        ReinforcementTurnProcessor(self.game, self.request_data).process_turn()

    def test_correctly_processes_turn(self):
        self.assertUnitIsInactive(self.par)
