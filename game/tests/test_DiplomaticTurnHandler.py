from game import models
from game.lib.ObjectsFromDatabase import ObjectsFromDatabase
from game.lib.StratagemTestCase import StratagemTestCase
from game.lib.turn_handlers.DiplomaticTurnHandler import DiplomaticTurnHandler


class DiplomaticTurnHandlerTestCase(StratagemTestCase):

    def setUp(self):
        self.game = models.Game(title="New Game")
        self.game.save()
        lvp = self.create_unit('Lvp', 'army', 'England')
        iri = self.create_unit('IRI', 'fleet', 'England')
        mid = self.create_unit('MAO', 'fleet', 'England')
        self.request_data = {'orders': {}, 'convoy_routes': []}
        self.create_convoy_route(lvp, 'Spa', 'NC', units=[iri, mid])
        self.handler = DiplomaticTurnHandler(self.game, self.request_data)

    def test_initializes_with_correct_values(self):
        self.assertEqual(self.handler.request_data, self.request_data)
        self.assertIsInstance(self.handler.db_objects, ObjectsFromDatabase)
        self.assertFalse(self.handler.retreat_phase_necessary)
        self.assertEqual(self.handler.orders, [])
        self.assertEqual(self.handler.convoy_routes, [])
        self.assertEqual(self.handler.locations, {})
        self.assertEqual(self.handler.supports, [])
        self.assertEqual(self.handler.conflicts, set())
        self.assertEqual(self.handler.displaced_units, [])
