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
        self.orders = []

    def create_custom_unit(self, terr_abbr, unit_type, country_name):
        new_unit = self.objects['game'].units.create(
            territory=self.get_terr(terr_abbr),
            unit_type=unit_type,
            country=self.objects['game'].countries.get(name=country_name)
        )
        self.objects['units'][new_unit.id] = new_unit
        return new_unit

    def get_unit_by_terr(self, terr_abbr):
        territory = self.get_terr(terr_abbr)
        for unit in self.objects['units'].values():
            if unit.territory == territory:
                return unit

    def get_terr(self, terr_abbr):
        return self.objects['territories'][terr_abbr]

    def hold(self, unit):
        data = {
            'unit_id': unit.id,
            'order_type': 'hold',
            'origin': unit.territory.abbreviation,
            'destination': unit.territory.abbreviation,
            'coast': unit.coast
        }
        self.orders.append(du.create_order_from_data(data, self.objects))

    def move(self, unit, destination, coast='', via_convoy=False):
        data = {
            'unit_id': unit.id,
            'order_type': 'move',
            'origin': unit.territory.abbreviation,
            'destination': destination,
            'coast': coast,
            'via_convoy': via_convoy
        }
        self.orders.append(du.create_order_from_data(data, self.objects))

    def support(self, unit, aux_unit, aux_order_type, aux_destination):
        data = {
            'unit_id': unit.id,
            'order_type': 'support',
            'origin': unit.territory.abbreviation,
            'destination': unit.territory.abbreviation,
            'coast': unit.coast,
            'aux_unit_id': aux_unit.id,
            'aux_order_type': aux_order_type,
            'aux_origin': aux_unit.territory.abbreviation,
            'aux_destination': aux_destination
        }
        self.orders.append(du.create_order_from_data(data, self.objects))

    def convoy(self, unit, aux_unit, aux_destination):
        data = {
            'unit_id': unit.id,
            'order_type': 'convoy',
            'origin': unit.territory.abbreviation,
            'destination': unit.territory.abbreviation,
            'coast': '',
            'aux_unit_id': aux_unit.id,
            'aux_order_type': 'move',
            'aux_origin': aux_unit.territory.abbreviation,
            'aux_destination': aux_destination
        }
        self.orders.append(du.create_order_from_data(data, self.objects))


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
        o = self.get_terr(self.data['origin'])
        d = self.get_terr(self.data['destination'])
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
        self.assertEqual(mapped_data['origin'], self.get_terr('Lon'))
        self.assertEqual(mapped_data['destination'], self.get_terr('Bre'))
        self.assertIn(self.eng_fleet, mapped_data['route'])


class MapOrdersToLocationsTestCase(BasicStratagemTest):

    def setUp(self):
        super().setUp()
        self.a_par = self.get_unit_by_terr('Par')
        self.a_mar = self.get_unit_by_terr('Mar')
        self.a_mun = self.get_unit_by_terr('Mun')
        self.move(self.a_par, 'Bur')
        self.support(self.a_mar, self.a_par, 'move', 'Bur')
        self.move(self.a_mun, 'Bur')

    def test_map_orders_to_locations(self):
        locations, supports, conflicts = du.map_orders_to_locations(self.orders)
        self.assertDictEqual(locations, {
            self.get_terr('Bur'): {
                self.a_par: 1,
                self.a_mun: 1
            },
            self.get_terr('Mar'): {
                self.a_mar: 1
            }
        })
        support_orders = [x for x in self.orders if x.order_type == 'support']
        self.assertEqual(supports, support_orders)
        self.assertEqual(conflicts, {self.get_terr('Bur')})


class ResolveConflictsInConvoyRouteTestCase(BasicStratagemTest):

    def setUp(self):
        super().setUp()
        self.f_TYS = self.create_custom_unit('TYS', 'fleet', 'France')
        self.f_ION = self.create_custom_unit('ION', 'fleet', 'France')
        self.a_Tun = self.create_custom_unit('Tun', 'army', 'France')
        self.f_ADR = self.create_custom_unit('ADR', 'fleet', 'Italy')
        self.f_Nap = self.get_unit_by_terr('Nap')

        self.move(self.a_Tun, 'Nap', via_convoy=True)
        self.convoy(self.f_ION, self.a_Tun, 'Nap')
        self.move(self.f_ADR, 'ION')
        self.support(self.f_Nap, self.f_ADR, 'move', 'ION')

        self.convoy_route = {
            'unit': self.a_Tun,
            'origin': self.a_Tun.territory,
            'destination': self.get_terr('Nap'),
            'route': [self.f_ION]
        }
        self.displaced_units = []

    def test_scenario_1(self):
        """
        This scenario follows the orders described above. The French
        army in Tun tries to convoy to Nap via ION, while the Italian
        fleet in ADR moves to ION with the support of Nap. Because there
        is only one convoy route between Tun and Nap, the support Nap
        gives to ADR doesn't get cut and the fleet in ION gets
        displaced.
        """
        locations, supports, conflicts = du.map_orders_to_locations(self.orders)
        other_routes = False

        resolved = du.resolve_conflicts_in_convoy_route(self.convoy_route,
                                                        locations, supports,
                                                        conflicts,
                                                        self.displaced_units,
                                                        other_routes)
        self.assertTrue(resolved)
        self.assertEqual(len(supports), 0)
        self.assertEqual(len(conflicts), 0)
        self.assertIn(self.f_ION, self.displaced_units)
        self.assertDictEqual(locations[self.get_terr('ION')],
                             {self.f_ADR: 2})

    def test_scenario_2(self):
        """
        This scenario is similar to the first, but with an added convoy
        route that prevents the currently examined route from being
        resolved.
        """

        self.convoy(self.f_TYS, self.a_Tun, 'Nap')
        locations, supports, conflicts = du.map_orders_to_locations(self.orders)
        other_routes = True
        resolved = du.resolve_conflicts_in_convoy_route(self.convoy_route,
                                                        locations, supports,
                                                        conflicts,
                                                        self.displaced_units,
                                                        other_routes)
        self.assertFalse(resolved)


class DetermineConvoyConflictOutcome(BasicStratagemTest):

    def setUp(self):
        super().setUp()
        self.f_TYS = self.create_custom_unit('TYS', 'fleet', 'France')
        self.f_ION = self.create_custom_unit('ION', 'fleet', 'France')
        self.a_Tun = self.create_custom_unit('Tun', 'army', 'France')
        self.f_ADR = self.create_custom_unit('ADR', 'fleet', 'Italy')
        self.f_Nap = self.get_unit_by_terr('Nap')

        self.move(self.a_Tun, 'Nap', via_convoy=True)
        self.convoy(self.f_ION, self.a_Tun, 'Nap')
        self.move(self.f_ADR, 'ION')

        self.convoy_route = {
            'unit': self.a_Tun,
            'origin': self.a_Tun.territory,
            'destination': self.get_terr('Nap'),
            'route': [self.f_ION]
        }

    def test_attacking_unit_wins(self):
        self.support(self.f_Nap, self.f_ADR, 'move', 'ION')
        locations, supports, conflicts = du.map_orders_to_locations(self.orders)
        units_in_terr = locations[self.get_terr('ION')]
        other_routes = False

        winner = du.determine_convoy_conflict_outcome(self.convoy_route,
                                                      self.f_ION, units_in_terr,
                                                      locations, supports,
                                                      conflicts, other_routes)
        self.assertEqual(winner, self.f_ADR)
        self.assertEqual(len(supports), 0)

    def test_defending_unit_wins(self):
        locations, supports, conflicts = du.map_orders_to_locations(self.orders)
        units_in_terr = locations[self.get_terr('ION')]
        other_routes = False
        winner = du.determine_convoy_conflict_outcome(self.convoy_route,
                                                      self.f_ION, units_in_terr,
                                                      locations, supports,
                                                      conflicts, other_routes)
        self.assertEqual(winner, self.f_ION)

    def test_conflict_is_deferred(self):
        self.support(self.f_Nap, self.f_ADR, 'move', 'ION')
        locations, supports, conflicts = du.map_orders_to_locations(self.orders)
        units_in_terr = locations[self.get_terr('ION')]
        other_routes = True
        winner = du.determine_convoy_conflict_outcome(self.convoy_route,
                                                      self.f_ION, units_in_terr,
                                                      locations, supports,
                                                      conflicts, other_routes)
        self.assertEqual(winner, 'defer')
        self.assertEqual(len(supports), 1)


class ReturnDefeatedUnitsToOriginsTestCase(BasicStratagemTest):

    def setUp(self):
        super().setUp()
        self.a_Par = self.get_unit_by_terr('Par')
        self.a_Mun = self.get_unit_by_terr('Mun')
        self.conflict_location = self.get_terr('Bur')
        self.displaced_units = []
        self.conflicts = set([])

    def test_all_units_repelled(self):
        self.move(self.a_Par, 'Bur')
        self.move(self.a_Mun, 'Bur')
        locations, supports, conflicts = du.map_orders_to_locations(self.orders)
        units_in_terr = locations[self.conflict_location]
        winner = None

        du.return_defeated_units_to_origins(self.conflict_location,
                                            units_in_terr, winner, locations,
                                            conflicts, self.displaced_units)
        self.assertDictEqual(locations[self.conflict_location], {})
        self.assertDictEqual(locations[self.get_terr('Par')], {self.a_Par: 1})
        self.assertDictEqual(locations[self.get_terr('Mun')], {self.a_Mun: 1})

    def test_winner_not_repelled(self):
        self.move(self.a_Par, 'Bur')
        self.move(self.a_Mun, 'Bur')
        locations, supports, conflicts = du.map_orders_to_locations(self.orders)
        units_in_terr = locations[self.conflict_location]
        winner = self.a_Par

        du.return_defeated_units_to_origins(self.conflict_location,
                                            units_in_terr, winner, locations,
                                            conflicts, self.displaced_units)
        self.assertDictEqual(locations[self.conflict_location], {self.a_Par: 1})
        self.assertDictEqual(locations[self.get_terr('Mun')], {self.a_Mun: 1})

    def test_losing_defender_displaced(self):
        self.a_Bur = self.create_custom_unit('Bur', 'army', 'France')
        self.hold(self.a_Bur)
        self.move(self.a_Mun, 'Bur')
        locations, supports, conflicts = du.map_orders_to_locations(self.orders)
        units_in_terr = locations[self.conflict_location]
        winner = self.a_Mun

        du.return_defeated_units_to_origins(self.conflict_location,
                                            units_in_terr, winner, locations,
                                            conflicts, self.displaced_units)
        self.assertDictEqual(locations[self.conflict_location], {self.a_Mun: 1})
        self.assertIn(self.a_Bur, self.displaced_units)

    def test_cannot_displace_own_unit(self):
        self.a_Bur = self.create_custom_unit('Bur', 'army', 'France')
        self.hold(self.a_Bur)
        self.move(self.a_Par, 'Bur')
        locations, supports, conflicts = du.map_orders_to_locations(self.orders)
        units_in_terr = locations[self.conflict_location]
        winner = self.a_Par
        du.return_defeated_units_to_origins(self.conflict_location,
                                            units_in_terr, winner, locations,
                                            conflicts, self.displaced_units)
        self.assertDictEqual(locations[self.conflict_location], {self.a_Bur: 1})
        self.assertDictEqual(locations[self.get_terr('Par')], {self.a_Par: 1})
        self.assertEqual(len(self.displaced_units), 0)
