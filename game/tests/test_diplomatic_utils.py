from django.test import TestCase
from game import models
from game.utils import diplomatic_utils


class CreateOrderFromDataTestCase(TestCase):

    def setUp(self):
        self.game = models.Game(title="New Game")
        self.game.save()
        par = self.game.territories.get(abbreviation="Par")
        self.unit = self.game.units.get(territory=par)
        self.data = {
            'unit_id': self.unit.id,
            'origin': 'Par',
            'destination': 'Bur',
            'order_type': 'move',
            'coast': ''
        }

    def test_create_basic_move_order(self):
        o = models.Territory.objects.get(abbreviation=self.data['origin'])
        d = models.Territory.objects.get(abbreviation=self.data['destination'])
        order = diplomatic_utils.create_order_from_data(self.data)
        self.assertEqual(order.turn, self.game.current_turn())
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