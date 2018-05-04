from game.utils import diplomatic_utils as du
from game.utils import test_utils as tu


class CreateOrderFromDataTestCase(tu.StratagemTest):

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
        order = du.create_order_from_data(self.data, self.objects)
        self.assertEqual(order.turn, self.objects['game'].current_turn())
        self.assertEqual(order.unit, self.unit)
        self.assertEqual(order.order_type, self.data['order_type'])
        self.assertEqual(order.origin, self.get_terr(self.data['origin']))
        self.assertEqual(order.destination,
                         self.get_terr(self.data['destination']))
        self.assertEqual(order.coast, self.data['coast'])
        self.assertIsNone(order.aux_unit)
        self.assertEqual(order.aux_order_type, '')
        self.assertIsNone(order.aux_origin)
        self.assertIsNone(order.aux_destination)
        self.assertFalse(order.via_convoy)


class CreateMissingHoldOrdersTestCase(tu.StratagemTest):

    def test_create_missing_hold_orders(self):
        orders = []
        du.create_missing_hold_orders(orders, self.objects)
        self.assertEqual(len(orders), len(self.objects['units']))


class MapConvoyRouteToModelsTestCase(tu.StratagemTest):

    def setUp(self):
        super().setUp()
        self.unit = self.get_unit_by_terr('Lon')
        self.f_eng = self.create_custom_unit('ENG', 'fleet', 'England')
        self.data = {
            'unit_id': self.unit.id,
            'origin': 'Lon',
            'destination': 'Bre',
            'route': [{'id': self.f_eng.id}]
        }

    def test_map_convoy_route_to_models(self):
        mapped_data = du.map_convoy_route_to_models(self.data, self.objects)
        self.assertEqual(mapped_data['unit'], self.unit)
        self.assertEqual(mapped_data['origin'], self.get_terr('Lon'))
        self.assertEqual(mapped_data['destination'], self.get_terr('Bre'))
        self.assertIn(self.f_eng, mapped_data['route'])


class MapOrdersToLocationsTestCase(tu.StratagemTest):

    def setUp(self):
        super().setUp()
        self.a_par = self.get_unit_by_terr('Par')
        self.a_mar = self.get_unit_by_terr('Mar')
        self.a_mun = self.get_unit_by_terr('Mun')

    def test_map_orders_to_locations(self):
        self.move(self.a_par, 'Bur')
        self.support(self.a_mar, self.a_par, 'move', 'Bur')
        self.move(self.a_mun, 'Bur')
        locations, supports, conflicts = du.map_orders_to_locations(self.orders)
        self.assertDictEqual(locations[self.get_terr('Bur')], {self.a_par: 1,
                                                               self.a_mun: 1})
        self.assertDictEqual(locations[self.get_terr('Mar')], {self.a_mar: 1})
        support_orders = [x for x in self.orders if x.order_type == 'support']
        self.assertEqual(supports, support_orders)
        self.assertEqual(conflicts, {self.get_terr('Bur')})


class ResolveConflictsInConvoyRouteTestCase(tu.StratagemTest):

    def setUp(self):
        super().setUp()
        self.f_tys = self.create_custom_unit('TYS', 'fleet', 'France')
        self.f_ion = self.create_custom_unit('ION', 'fleet', 'France')
        self.a_tun = self.create_custom_unit('Tun', 'army', 'France')
        self.f_adr = self.create_custom_unit('ADR', 'fleet', 'Italy')
        self.f_nap = self.get_unit_by_terr('Nap')
        self.move(self.a_tun, 'Nap', via_convoy=True)
        self.convoy(self.f_ion, self.a_tun, 'Nap')
        self.move(self.f_adr, 'ION')
        self.support(self.f_nap, self.f_adr, 'move', 'ION')
        self.convoy_route = {
            'unit': self.a_tun,
            'origin': self.a_tun.territory,
            'destination': self.get_terr('Nap'),
            'route': [self.f_ion]
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
        self.assertIn(self.f_ion, self.displaced_units)
        self.assertDictEqual(locations[self.get_terr('ION')],
                             {self.f_adr: 2})

    def test_scenario_2(self):
        """
        This scenario is similar to the first, but with an added convoy
        route that prevents the currently examined route from being
        resolved.
        """

        self.convoy(self.f_tys, self.a_tun, 'Nap')
        locations, supports, conflicts = du.map_orders_to_locations(self.orders)
        other_routes = True
        resolved = du.resolve_conflicts_in_convoy_route(self.convoy_route,
                                                        locations, supports,
                                                        conflicts,
                                                        self.displaced_units,
                                                        other_routes)
        self.assertFalse(resolved)


class DetermineConvoyConflictOutcome(tu.StratagemTest):

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


class ReturnDefeatedUnitsToOriginsTestCase(tu.StratagemTest):

    def setUp(self):
        super().setUp()
        self.a_par = self.get_unit_by_terr('Par')
        self.a_mun = self.get_unit_by_terr('Mun')
        self.conflict_location = self.get_terr('Bur')
        self.displaced_units = []
        self.conflicts = set([])

    def test_all_units_repelled(self):
        self.move(self.a_par, 'Bur')
        self.move(self.a_mun, 'Bur')
        locations, supports, conflicts = du.map_orders_to_locations(self.orders)
        units_in_terr = locations[self.conflict_location]
        winner = None

        du.return_defeated_units_to_origins(self.conflict_location,
                                            units_in_terr, winner, locations,
                                            conflicts, self.displaced_units)
        self.assertDictEqual(locations[self.conflict_location], {})
        self.assertDictEqual(locations[self.get_terr('Par')], {self.a_par: 1})
        self.assertDictEqual(locations[self.get_terr('Mun')], {self.a_mun: 1})

    def test_winner_not_repelled(self):
        self.move(self.a_par, 'Bur')
        self.move(self.a_mun, 'Bur')
        locations, supports, conflicts = du.map_orders_to_locations(self.orders)
        units_in_terr = locations[self.conflict_location]
        winner = self.a_par

        du.return_defeated_units_to_origins(self.conflict_location,
                                            units_in_terr, winner, locations,
                                            conflicts, self.displaced_units)
        self.assertDictEqual(locations[self.conflict_location], {self.a_par: 1})
        self.assertDictEqual(locations[self.get_terr('Mun')], {self.a_mun: 1})

    def test_losing_defender_displaced(self):
        a_bur = self.create_custom_unit('Bur', 'army', 'France')
        self.hold(a_bur)
        self.move(self.a_mun, 'Bur')
        locations, supports, conflicts = du.map_orders_to_locations(self.orders)
        units_in_terr = locations[self.conflict_location]
        winner = self.a_mun

        du.return_defeated_units_to_origins(self.conflict_location,
                                            units_in_terr, winner, locations,
                                            conflicts, self.displaced_units)
        self.assertDictEqual(locations[self.conflict_location], {self.a_mun: 1})
        self.assertIn(a_bur, self.displaced_units)

    def test_cannot_displace_own_unit(self):
        a_bur = self.create_custom_unit('Bur', 'army', 'France')
        self.hold(a_bur)
        self.move(self.a_par, 'Bur')
        locations, supports, conflicts = du.map_orders_to_locations(self.orders)
        units_in_terr = locations[self.conflict_location]
        winner = self.a_par
        du.return_defeated_units_to_origins(self.conflict_location,
                                            units_in_terr, winner, locations,
                                            conflicts, self.displaced_units)
        self.assertDictEqual(locations[self.conflict_location], {a_bur: 1})
        self.assertDictEqual(locations[self.get_terr('Par')], {self.a_par: 1})
        self.assertEqual(len(self.displaced_units), 0)


class ReturnUnitToOriginTestCase(tu.StratagemTest):

    def setUp(self):
        super().setUp()
        self.a_par = self.get_unit_by_terr('Par')
        self.move(self.a_par, 'Bur')

    def test_unit_gets_returned_to_origin(self):
        locations, _, conflicts = du.map_orders_to_locations(self.orders)
        du.return_unit_to_origin(self.a_par, locations, conflicts)
        self.assertDictEqual(locations[self.get_terr('Par')], {self.a_par: 1})

    def test_can_add_unit_origin_to_conflicts(self):
        a_gas = self.create_custom_unit('Gas', 'army', 'France')
        self.move(a_gas, 'Par')
        locations, _, conflicts = du.map_orders_to_locations(self.orders)
        du.return_unit_to_origin(self.a_par, locations, conflicts)
        self.assertIn(self.get_terr('Par'), conflicts)


class AddSupportsTestCase(tu.StratagemTest):

    def setUp(self):
        super().setUp()
        self.a_par = self.get_unit_by_terr('Par')
        self.a_mar = self.get_unit_by_terr('Mar')
        self.support(self.a_mar, self.a_par, 'move', 'Bur')

    def test_adds_support_to_unit(self):
        self.move(self.a_par, 'Bur')
        locations, supports, conflicts = du.map_orders_to_locations(self.orders)
        du.add_supports(locations, supports, conflicts)
        self.assertDictEqual(locations[self.get_terr('Bur')], {self.a_par: 2})

    def test_doesnt_add_support_to_nonexistent_order(self):
        self.hold(self.a_par)
        locations, supports, conflicts = du.map_orders_to_locations(self.orders)
        du.add_supports(locations, supports, conflicts)
        with self.assertRaises(KeyError):
            print(locations[self.get_terr('Bur')])


class CheckForIllegalSwapsTestCase(tu.StratagemTest):

    def setUp(self):
        super().setUp()
        self.a_ven = self.get_unit_by_terr('Ven')
        self.a_tri = self.get_unit_by_terr('Tri')
        self.move(self.a_ven, 'Tri')
        self.move(self.a_tri, 'Ven')

    def test_returns_equally_powerful_units_to_origins(self):
        locations, supports, conflicts = du.map_orders_to_locations(self.orders)
        du.add_supports(locations, supports, conflicts)
        du.check_for_illegal_swaps(self.orders, locations, conflicts)
        self.assertDictEqual(locations[self.get_terr('Ven')], {self.a_ven: 1})
        self.assertDictEqual(locations[self.get_terr('Tri')], {self.a_tri: 1})

    def test_returns_only_less_powerful_unit_to_origin(self):
        a_tyr = self.create_custom_unit('Tyr', 'army', 'Austria')
        self.support(a_tyr, self.a_tri, 'move', 'Ven')
        locations, supports, conflicts = du.map_orders_to_locations(self.orders)
        du.add_supports(locations, supports, conflicts)
        du.check_for_illegal_swaps(self.orders, locations, conflicts)
        self.assertDictEqual(locations[self.get_terr('Ven')],
                             {self.a_tri: 2, self.a_ven: 1})


class ResolveConflictTestCase(tu.StratagemTest):

    def test_resolves_conflicts(self):
        conflict_location = self.get_terr('Bur')
        a_par = self.get_unit_by_terr('Par')
        a_mar = self.get_unit_by_terr('Mar')
        a_mun = self.get_unit_by_terr('Mun')
        a_bel = self.create_custom_unit('Bel', 'army', 'Germany')
        self.move(a_par, 'Bur')
        self.support(a_mar, a_par, 'move', 'Bur')
        self.move(a_mun, 'Bur')
        self.support(a_bel, a_mun, 'move', 'Bur')
        locations, supports, conflicts = du.map_orders_to_locations(self.orders)
        du.add_supports(locations, supports, conflicts)
        du.resolve_conflict(conflict_location, locations, conflicts,
                            displaced_units=[])
        self.assertDictEqual(locations[self.get_terr('Par')], {a_par: 1})
        self.assertDictEqual(locations[self.get_terr('Mar')], {a_mar: 1})
        self.assertDictEqual(locations[self.get_terr('Mun')], {a_mun: 1})
        self.assertDictEqual(locations[self.get_terr('Bel')], {a_bel: 1})


class DetermineConflictOutcomeTestCase(tu.StratagemTest):

    def setUp(self):
        super().setUp()
        self.f_tri = self.get_unit_by_terr('Tri')
        self.a_ven = self.get_unit_by_terr('Ven')

    def test_winner_is_defender(self):
        units_in_terr = {self.f_tri: 1, self.a_ven: 1}
        winner = du.determine_conflict_outcome(self.a_ven, units_in_terr)
        self.assertEqual(winner, self.a_ven)

    def test_winner_is_not_defender(self):
        units_in_terr = {self.f_tri: 2, self.a_ven: 1}
        winner = du.determine_conflict_outcome(self.a_ven, units_in_terr)
        self.assertEqual(winner, self.f_tri)

    def test_no_winner(self):
        units_in_terr = {self.f_tri: 1, self.a_ven: 1}
        winner = du.determine_conflict_outcome(None, units_in_terr)
        self.assertIsNone(winner)


class UpdateUnitLocations(tu.StratagemTest):

    def test_unit_positions_get_updated(self):
        f_mao = self.create_custom_unit('MAO', 'fleet', 'England')
        a_spa = self.create_custom_unit('Spa', 'army', 'England')
        a_gas = self.create_custom_unit('Gas', 'army', 'France')
        self.move(a_spa, 'Gas')
        self.move(f_mao, 'Spa', coast='NC')
        locations = {self.get_terr('Gas'): {a_spa: 2},
                     self.get_terr('Spa'): {f_mao: 1}}
        displaced_units = [a_gas]
        du.update_unit_locations(locations, displaced_units, self.orders)
        self.assertEqual(f_mao.territory, self.get_terr('Spa'))
        self.assertEqual(f_mao.coast, 'NC')
        self.assertEqual(a_spa.territory, self.get_terr('Gas'))
        self.assertIsNone(a_gas.territory)
        self.assertEqual(a_gas.retreating_from, self.get_terr('Gas'))
