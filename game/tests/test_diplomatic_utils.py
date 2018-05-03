from django.test import TestCase
from game import models
from game.utils import diplomatic_utils as du


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


class CreateMissingHoldOrdersTestCase(TestCase):

    def setUp(self):
        game = models.Game(title="New Game")
        game.save()
        self.objects = {
            'game': game,
            'units': {u.id: u for u in game.units.filter(active=True)},
            'territories': {t.abbreviation: t for t in
                            game.territories.all()}
        }

    def test_create_missing_hold_orders(self):
        orders = []
        du.create_missing_hold_orders(orders, self.objects)
        self.assertEqual(len(orders), len(self.objects['units']))


class MapConvoyRouteToModelsTestCase(TestCase):

    def setUp(self):
        game = models.Game(title="New Game")
        game.save()
        self.objects = {
            'game': game,
            'units': {u.id: u for u in game.units.filter(active=True)},
            'territories': {t.abbreviation: t for t in
                            game.territories.all()}
        }
        self.unit = game.units.get(territory=self.objects['territories']['Lon'])
        self.eng_fleet = game.units.create(
            territory=self.objects['territories']['ENG'], unit_type='fleet',
            country=game.countries.get(name='England')
        )
        self.objects['units'][self.eng_fleet.id] = self.eng_fleet
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


class MapOrdersToLocationsTestCase(TestCase):

    def setUp(self):
        game = models.Game(title="New Game")
        game.save()
        self.objects = {
            'game': game,
            'units': {u.id: u for u in game.units.filter(active=True)},
            'territories': {t.abbreviation: t for t in
                            game.territories.all()}
        }
        self.a_par = game.units.get(
            territory=self.objects['territories']['Par'])
        self.a_mar = game.units.get(
            territory=self.objects['territories']['Mar'])
        self.a_mun = game.units.get(
            territory=self.objects['territories']['Mun'])
        order_data = [
            {'unit_id': self.a_par.id, 'order_type': 'move', 'origin': 'Par',
             'destination': 'Bur', 'coast': ''},
            {'unit_id': self.a_mar.id, 'order_type': 'support', 'origin': 'Mar',
             'destination': 'Mar', 'coast': '', 'aux_unit': self.a_par.id,
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


