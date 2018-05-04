from game.utils import reinforcement_utils as ru
from game.utils import test_utils as tu


class CreateReinforcementOrderFromDataTestCase(tu.StratagemTest):

    def test_can_create_units(self):
        # Delete old unit so we have room to create new one.
        old_unit = self.get_unit_by_terr('Stp')
        old_unit.deactivate()

        data = {
            'order_type': 'create',
            'territory': 'Stp',
            'country': 'Russia',
            'unit_type': 'fleet',
            'coast': 'SC'
        }
        order = ru.create_reinforcement_order_from_data(data, self.objects)
        # Since unit is newly created, it won't be in the objects dict.
        unit = self.objects['game'].units.get(active=True,
                                              territory=self.get_terr('Stp'))
        self.assertEqual(order.turn, self.objects['game'].current_turn())
        self.assertEqual(order.unit, unit)
        self.assertEqual(order.order_type, 'create')
        self.assertEqual(order.origin, self.get_terr('Stp'))
        self.assertEqual(order.coast, 'SC')
        self.assertTrue(unit.active)
        self.assertEqual(unit.territory, self.get_terr('Stp'))
        self.assertEqual(unit.coast, 'SC')

    def test_can_delete_units(self):
        unit = self.get_unit_by_terr('Stp')
        data = {
            'order_type': 'delete',
            'territory': 'Stp',
            'unit_id': unit.id
        }

        order = ru.create_reinforcement_order_from_data(data, self.objects)
        self.assertEqual(order.turn, self.objects['game'].current_turn())
        self.assertEqual(order.unit, unit)
        self.assertEqual(order.order_type, 'delete')
        self.assertEqual(order.origin, self.get_terr('Stp'))
        self.assertFalse(unit.active)