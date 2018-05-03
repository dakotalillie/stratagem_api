from django.test import TestCase
from game import models
from game.utils import diplomatic_utils as du


class BasicStratagemTest(TestCase):
    
    def setUp(self):
        game = models.Game(title="New Game")
        game.save()
        self.objects = {
            'game': game,
            'units': {u.id: u for u in game.units.filter(active=True)},
            'territories': {t.abbreviation: t for t in
                            game.territories.all()}
        }

    def create_custom_unit(self, terr_abbr, unit_type, country_name):
        new_unit = self.objects['game'].units.create(
            territory=self.objects['territories'][terr_abbr],
            unit_type=unit_type,
            country=self.objects['game'].countries.get(name=country_name)
        )
        self.objects['units'][new_unit.id] = new_unit
        return new_unit

    def get_unit_by_terr(self, terr_abbr):
        territory = self.objects['territories'][terr_abbr]
        for unit in self.objects['units'].values():
            if unit.territory == territory:
                return unit


class CreateOrderFromDataTestCase(BasicStratagemTest):

    def setUp(self):
        super().setUp()
        self.unit = self.get_unit_by_terr('Par')
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
        order = du.create_order_from_data(self.data, self.objects)
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


class CreateMissingHoldOrdersTestCase(BasicStratagemTest):

    def test_create_missing_hold_orders(self):
        orders = []
        du.create_missing_hold_orders(orders, self.objects)
        self.assertEqual(len(orders), len(self.objects['units']))


class MapConvoyRouteToModelsTestCase(BasicStratagemTest):

    def setUp(self):
        super().setUp()
        self.unit = self.get_unit_by_terr('Lon')
        self.eng_fleet = self.create_custom_unit('ENG', 'fleet', 'England')
        self.data = {
            'unit_id': self.unit.id,
            'origin': 'Lon',
            'destination': 'Bre',
            'route': [{'id': self.eng_fleet.id}]
        }

    def test_map_convoy_route_to_models(self):
        mapped_data = du.map_convoy_route_to_models(self.data, self.objects)
        self.assertEqual(mapped_data['unit'], self.unit)
        self.assertEqual(mapped_data['origin'],
                         self.objects['territories']['Lon'])
        self.assertEqual(mapped_data['destination'],
                         self.objects['territories']['Bre'])
        self.assertIn(self.eng_fleet, mapped_data['route'])


class MapOrdersToLocationsTestCase(BasicStratagemTest):

    def setUp(self):
        super().setUp()
        self.a_par = self.get_unit_by_terr('Par')
        self.a_mar = self.get_unit_by_terr('Mar')
        self.a_mun = self.get_unit_by_terr('Mun')
        order_data = [
            {'unit_id': self.a_par.id, 'order_type': 'move', 'origin': 'Par',
             'destination': 'Bur', 'coast': ''},
            {'unit_id': self.a_mar.id, 'order_type': 'support', 'origin': 'Mar',
             'destination': 'Mar', 'coast': '', 'aux_unit_id': self.a_par.id,
             'aux_order_type': 'move', 'aux_origin': 'Par',
             'aux_destination': 'Bur'},
            {'unit_id': self.a_mun.id, 'order_type': 'move', 'origin': 'Mun',
             'destination': 'Bur', 'coast': ''}
        ]
        self.orders = [du.create_order_from_data(data, self.objects)
                       for data in order_data]

    def test_map_orders_to_locations(self):
        locations, supports, conflicts = du.map_orders_to_locations(self.orders)
        self.assertDictEqual(locations, {
            self.objects['territories']['Bur']: {
                self.a_par: 1,
                self.a_mun: 1
            },
            self.objects['territories']['Mar']: {
                self.a_mar: 1
            }
        })
        support_orders = [x for x in self.orders if x.order_type == 'support']
        self.assertEqual(supports, support_orders)
        self.assertEqual(conflicts, {self.objects['territories']['Bur']})


class ResolveConflictsInConvoyRoute(BasicStratagemTest):

    def setUp(self):
        super().setUp()
        self.f_TYS = self.create_custom_unit('TYS', 'fleet', 'France')
        self.f_ION = self.create_custom_unit('ION', 'fleet', 'France')
        self.a_Tun = self.create_custom_unit('Tun', 'army', 'France')
        self.f_ADR = self.create_custom_unit('ADR', 'fleet', 'Italy')
        self.f_Nap = self.get_unit_by_terr('Nap')

        order_data = [
            {
                 'unit_id': self.a_Tun.id,
                 'order_type': 'move',
                 'origin': 'Tun',
                 'destination': 'Nap',
                 'coast': '',
                 'via_convoy': True
            },
            {
                 'unit_id': self.f_ION.id,
                 'order_type': 'convoy',
                 'origin': 'ION',
                 'destination': 'ION',
                 'coast': '',
                 'aux_unit_id': self.a_Tun.id,
                 'aux_order_type': 'move',
                 'aux_origin': 'Tun',
                 'aux_destination': 'Nap'
            },
            {
                 'unit_id': self.f_ADR.id,
                 'order_type': 'move',
                 'origin': 'ADR',
                 'destination': 'ION',
                 'coast': ''
            },
            {
                 'unit_id': self.f_Nap.id,
                 'order_type': 'support',
                 'origin': 'Nap',
                 'destination': 'Nap',
                 'coast': '',
                 'aux_unit_id': self.f_ADR.id,
                 'aux_order_type': 'move',
                 'aux_origin': 'ADR',
                 'aux_destination': 'ION'
            },
        ]
        self.orders = [du.create_order_from_data(data, self.objects)
                  for data in order_data]

    def test_scenario_1(self):
        """
        This scenario follows the orders described above. The French
        army in Tun tries to convoy to Nap via ION, while the Italian
        fleet in ADR moves to ION with the support of Nap. Because there
        is only one convoy route between Tun and Nap, the support Nap
        gives to ADR doesn't get cut and the fleet in ION gets
        displaced.
        """
        convoy_route = {
            'unit': self.a_Tun,
            'origin': self.a_Tun.territory,
            'destination': self.objects['territories']['Nap'],
            'route': [self.f_ION]
        }
        locations, supports, conflicts = du.map_orders_to_locations(self.orders)
        displaced_units = []
        other_routes = False

        resolved = du.resolve_conflicts_in_convoy_route(convoy_route, locations,
                                                        supports, conflicts,
                                                        displaced_units,
                                                        other_routes)
        self.assertTrue(resolved)
        self.assertEqual(len(supports), 0)
        self.assertEqual(len(conflicts), 0)
        self.assertIn(self.f_ION, displaced_units)
        self.assertDictEqual(locations[self.objects['territories']['ION']],
                             {self.f_ADR: 2})

