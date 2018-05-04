from game.utils import test_utils as tu
from game.utils import update_turn_utils as utu


class CreateNewTurnTestCase(tu.StratagemTest):

    def test_diplomatic_to_retreat(self):
        turn = utu.create_new_turn(self.objects['game'],
                                   self.objects['game'].current_turn(),
                                   retreat_phase_necessary=True)
        self.assertEqual(turn.year, 1901)
        self.assertEqual(turn.season, 'spring')
        self.assertEqual(turn.phase, 'retreat')

    def test_diplomatic_to_reinforcement(self):
        old_turn = self.objects['game'].turns.create(year=1901, season='fall',
                                                     phase='diplomatic')
        turn = utu.create_new_turn(self.objects['game'], old_turn,
                                   retreat_phase_necessary=False)
        self.assertEqual(turn.year, 1901)
        self.assertEqual(turn.season, 'fall')
        self.assertEqual(turn.phase, 'reinforcement')

    def test_diplomatic_to_diplomatic(self):
        turn = utu.create_new_turn(self.objects['game'],
                                   self.objects['game'].current_turn(),
                                   retreat_phase_necessary=False)
        self.assertEqual(turn.year, 1901)
        self.assertEqual(turn.season, 'fall')
        self.assertEqual(turn.phase, 'diplomatic')

    def test_retreat_to_diplomatic(self):
        old_turn = self.objects['game'].turns.create(year=1901, season='spring',
                                                     phase='retreat')
        turn = utu.create_new_turn(self.objects['game'], old_turn,
                                   retreat_phase_necessary=False)
        self.assertEqual(turn.year, 1901)
        self.assertEqual(turn.season, 'fall')
        self.assertEqual(turn.phase, 'diplomatic')

    def test_retreat_to_reinforcement(self):
        old_turn = self.objects['game'].turns.create(year=1901, season='fall',
                                                     phase='retreat')
        turn = utu.create_new_turn(self.objects['game'], old_turn,
                                   retreat_phase_necessary=False)
        self.assertEqual(turn.year, 1901)
        self.assertEqual(turn.season, 'fall')
        self.assertEqual(turn.phase, 'reinforcement')

    def test_reinforcement_to_diplomatic(self):
        old_turn = self.objects['game'].turns.create(year=1901, season='fall',
                                                     phase='reinforcement')
        turn = utu.create_new_turn(self.objects['game'], old_turn,
                                   retreat_phase_necessary=False)
        self.assertEqual(turn.year, 1902)
        self.assertEqual(turn.season, 'spring')
        self.assertEqual(turn.phase, 'diplomatic')


class UpdateTerritoryOwnersTestCase(tu.StratagemTest):

    def test_updates_territory_owner(self):
        unit = self.create_custom_unit('Spa', 'army', 'France')
        utu.update_territory_owners(self.objects['game'])
        spa = self.objects['game'].territories.get(abbreviation="Spa")
        self.assertEqual(spa.owner, unit.country)

    def test_doesnt_update_water_territory_owner(self):
        self.create_custom_unit('MAO', 'fleet', 'France')
        utu.update_territory_owners(self.objects['game'])
        mao = self.objects['game'].territories.get(abbreviation="MAO")
        self.assertIsNone(mao.owner)