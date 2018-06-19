from game.lib import StratagemTestCase
from game.lib.turn_processors import RetreatTurnProcessor


class SimpleRetreatMoveTestCase(StratagemTestCase):

    def setUp(self):
        super().setUp()
        self.set_current_turn(1901, 'fall', 'retreat')
        self.gas = self.create_displaced_unit('army', 'France', 'Gas', 'Mun')
        self.move_displaced(self.gas, 'Pic')
        RetreatTurnProcessor(self.game, self.request_data).process_turn()

    def test_correctly_processes_turn(self):
        self.assertUnitInTerritory(self.gas, 'Pic')


class SimpleDeleteMoveTestCase(StratagemTestCase):

    def setUp(self):
        super().setUp()
        self.set_current_turn(1902, 'spring', 'retreat')
        self.tri = self.create_displaced_unit('army', 'Austria', 'Tri', 'Vie')
        self.delete(self.tri)
        RetreatTurnProcessor(self.game, self.request_data).process_turn()

    def test_correctly_processes_turn(self):
        self.assertUnitIsInactive(self.tri)


class SameMoveDestinationTestCase(StratagemTestCase):

    def setUp(self):
        super().setUp()
        self.set_current_turn(1902, 'fall', 'retreat')
        self.mun = self.create_displaced_unit('army', 'Germany', 'Mun', 'Tyr')
        self.par = self.create_displaced_unit('army', 'France', 'Par', 'Bre')
        self.move_displaced(self.mun, 'Bur')
        self.move_displaced(self.par, 'Bur')
        RetreatTurnProcessor(self.game, self.request_data).process_turn()

    def test_correctly_processes_turn(self):
        self.assertUnitIsInactive(self.mun)
        self.assertUnitIsInactive(self.par)


class DefaultDeleteOrderTestCase(StratagemTestCase):

    def setUp(self):
        super().setUp()
        self.set_current_turn(1901, 'fall', 'retreat')
        self.sev = self.create_displaced_unit('fleet', 'Russia', 'Sev', 'BLA')
        RetreatTurnProcessor(self.game, self.request_data).process_turn()

    def test_correctly_processes_turn(self):
        self.assertUnitIsInactive(self.sev)
