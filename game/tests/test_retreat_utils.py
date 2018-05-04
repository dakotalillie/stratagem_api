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


class CreateMissingDeleteOrdersTestCase(tu.StratagemTest):

    def test_creates_missing_delete_order(self):
        unit = self.create_custom_unit('Gal', 'army', 'Russia')
        unit.displace(self.get_terr('Vie'))
        ru.create_missing_delete_orders(self.orders, self.objects)
        self.assertEqual(len(self.orders), 1)
        order = self.orders[0]
        unit = order.unit
        self.assertEqual(order.turn, self.objects['game'].current_turn())
        self.assertEqual(order.unit, unit)
        self.assertEqual(order.order_type, 'delete')
        self.assertEqual(order.origin, self.get_terr('Gal'))
        self.assertIsNone(unit.retreating_from)
        self.assertIsNone(unit.invaded_from)
        self.assertFalse(unit.active)


class HandleRetreatConflictsTestCase(tu.StratagemTest):

    def test_handles_retreat_conflicts(self):
        a_gal = self.create_custom_unit('Gal', 'army', 'Russia')
        a_pru = self.create_custom_unit('Pru', 'army', 'Germany')
        a_ukr = self.create_custom_unit('Ukr', 'army', 'Turkey')
        a_gal.displace(self.get_terr('Vie'))
        a_pru.displace(self.get_terr('Ber'))
        a_ukr.displace(self.get_terr('Sev'))
        self.move_displaced(a_gal, 'War')
        self.move_displaced(a_pru, 'War')
        self.move_displaced(a_ukr, 'Gal')
        locations = ru.handle_retreat_conflicts(self.orders)
        self.assertEqual(locations[self.get_terr('Gal')], [a_ukr])
        with self.assertRaises(KeyError):
            print(locations[self.get_terr('War')])
        self.assertFalse(a_gal.active)
        self.assertFalse(a_pru.active)


class UpdateRetreatUnitLocations(tu.StratagemTest):

    def test_updates_unit_location(self):
        unit = self.create_custom_unit('MAO', 'fleet', 'France')
        unit.displace(self.get_terr('ENG'))
        self.move_displaced(unit, 'Spa', 'NC')
        locations = {self.get_terr('Spa'): [unit]}
        ru.update_retreat_unit_locations(locations, self.orders)
        self.assertEqual(unit.territory, self.get_terr('Spa'))
        self.assertEqual(unit.coast, 'NC')
        self.assertIsNone(unit.retreating_from)
        self.assertIsNone(unit.invaded_from)