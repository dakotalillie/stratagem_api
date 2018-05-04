from game.utils import retreat_utils as ru
from game.utils import test_utils as tu


class CreateRetreatOrderFromDataTestCase(tu.StratagemTest):

    def setUp(self):
        super().setUp()
        self.unit = self.create_custom_unit('Gal', 'army', 'Russia')
        self.unit.displace(self.get_terr('Vie'))

    def test_create_move_order(self):
        data = {
            'unit_id': self.unit.id,
            'origin': 'Gal',
            'destination': 'War',
            'order_type': 'move',
            'coast': ''
        }
        order = ru.create_retreat_order_from_data(data, self.objects)
        self.assertEqual(order.turn, self.objects['game'].current_turn())
        self.assertEqual(order.unit, self.unit)
        self.assertEqual(order.order_type, data['order_type'])
        self.assertEqual(order.origin, self.get_terr(data['origin']))
        self.assertEqual(order.destination, self.get_terr(data['destination']))
        self.assertEqual(order.coast, data['coast'])

    def test_create_delete_order(self):
        data = {
            'unit_id': self.unit.id,
            'order_type': 'delete',
            'territory': 'Gal'
        }
        order = ru.create_retreat_order_from_data(data, self.objects)
        self.assertEqual(order.turn, self.objects['game'].current_turn())
        self.assertEqual(order.unit, self.unit)
        self.assertEqual(order.order_type, data['order_type'])
        self.assertEqual(order.origin, self.get_terr(data['territory']))
        self.assertIsNone(self.unit.retreating_from)
        self.assertIsNone(self.unit.invaded_from)
        self.assertFalse(self.unit.active)