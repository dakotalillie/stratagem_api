from game.lib import StratagemTestCase
from game.lib.turn_processors import RetreatTurnProcessor


class SimpleRetreatMoveTestCase(StratagemTestCase):

    def setUp(self):
        super().setUp()
        self.set_current_turn(1901, 'fall', 'retreat')
        self.gas = self.create_displaced_unit('army', 'France', 'Gas', 'Mun')
        self.issue_move_order(self.gas, 'Pic')
        RetreatTurnProcessor(self.game, self.request_data).process_turn()

    def test_correctly_processes_turn(self):
        self.assertUnitInTerritory(self.gas, 'Pic')


class SimpleDeleteMoveTestCase(StratagemTestCase):

    def setUp(self):
        super().setUp()
        self.set_current_turn(1902, 'spring', 'retreat')
        self.tri = self.create_displaced_unit('army', 'Austria', 'Tri', 'Vie')
        self.issue_delete_order(self.tri)
        RetreatTurnProcessor(self.game, self.request_data).process_turn()

    def test_correctly_processes_turn(self):
        self.assertUnitIsInactive(self.tri)


class SameMoveDestinationTestCase(StratagemTestCase):

    def setUp(self):
        super().setUp()
        self.set_current_turn(1902, 'fall', 'retreat')
        self.mun = self.create_displaced_unit('army', 'Germany', 'Mun', 'Tyr')
        self.par = self.create_displaced_unit('army', 'France', 'Par', 'Bre')
        self.issue_move_order(self.mun, 'Bur')
        self.issue_move_order(self.par, 'Bur')
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


class UpdateTurnTestCase1(StratagemTestCase):
    """
    If current season is spring, transitions to diplomatic phase in fall.
    """

    def setUp(self):
        super().setUp()
        self.set_current_turn(1901, 'spring', 'retreat')
        RetreatTurnProcessor(self.game, self.request_data).process_turn()

    def test_correctly_processes_turn(self):
        self.assertCurrentTurn(1901, 'fall', 'diplomatic')


class UpdateTurnTestCase2(StratagemTestCase):
    """
    If current season is fall, transitions to reinforcement phase.
    """

    def setUp(self):
        super().setUp()
        self.set_current_turn(1901, 'fall', 'retreat')
        RetreatTurnProcessor(self.game, self.request_data).process_turn()

    def test_correctly_processes_turn(self):
        self.assertCurrentTurn(1901, 'fall', 'reinforcement')