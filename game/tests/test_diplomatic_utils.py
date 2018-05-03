from django.test import TestCase
from game import models
from game.utils import diplomatic_utils


class CreateOrderFromDataTestCase(TestCase):

    def setUp(self):
        game = models.Game(title="New Game")
        game.save()
        self.objects = {
            'game': game,
            'units': {u.id: u for u in game.units.filter(active=True)},
            'territories': {t.abbreviation: t for t in
                            game.territories.all()}
        }
        self.unit = game.units.get(territory=self.objects['territories']['Par'])
        self.data = {
            'unit_id': self.unit.id,
            'origin': 'Par',
            'destination': 'Bur',
            'order_type': 'move',
            'coast': ''
        }

    def test_create_basic_move_order(self):
        o = self.objects['territories'][self.data['origin']]
        d = self.objects['territories'][self.data['destination']]
        order = diplomatic_utils.create_order_from_data(self.data, self.objects)
        self.assertEqual(order.turn, self.objects['game'].current_turn())
        self.assertEqual(order.unit, models.Unit.objects.get(pk=self.unit.id))
        self.assertEqual(order.order_type, self.data['order_type'])
        self.assertEqual(order.origin, o)
        self.assertEqual(order.destination, d)
        self.assertEqual(order.coast, self.data['coast'])
        self.assertIsNone(order.aux_unit)
        self.assertEqual(order.aux_order_type, '')
        self.assertIsNone(order.aux_origin)
        self.assertIsNone(order.aux_destination)
        self.assertFalse(order.via_convoy)


class CreateMissingHoldOrdersTestCase(TestCase):

    def setUp(self):
        self.game = models.Game(title="New Game")
        self.game.save()

    def test_create_missing_hold_orders(self):
        orders = []
        diplomatic_utils.create_missing_hold_orders(self.game, orders)
        self.assertEqual(len(orders), self.game.units.count())

