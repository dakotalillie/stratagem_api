from django.test import TestCase
from game import models


class StratagemTestCase(TestCase):

    def setUp(self):
        self.game = models.Game(title="New Game")
        self.game.save()
        self.request_data = {'orders': {}, 'convoy_routes': []}

    def set_current_turn(self, year, season, phase):
        self.game.turns.create(year=year, season=season, phase=phase)

    def create_unit(self, terr_abbr, unit_type, country_name):
        return self.game.units.create(
            territory=self.get_terr(terr_abbr),
            unit_type=unit_type,
            country=self.game.countries.get(name=country_name)
        )

    def create_displaced_unit(self, unit_type, country_name,
                              retreating_from, invaded_from):
        return self.game.units.create(
            unit_type=unit_type,
            country=self.game.countries.get(name=country_name),
            retreating_from=self.get_terr(retreating_from),
            invaded_from=self.get_terr(invaded_from)
        )

    def get_unit(self, id):
        return self.game.units.get(pk=id)

    def get_terr(self, terr_abbr):
        return self.game.territories.get(abbreviation=terr_abbr)

    def hold(self, unit):
        self.request_data['orders'][unit.id] = {
            'unit_id': str(unit.id),
            'order_type': 'hold',
            'origin': unit.territory.abbreviation,
            'destination': unit.territory.abbreviation,
            'coast': unit.coast
        }

    def move(self, unit, destination, coast='', via_convoy=False):
        self.request_data['orders'][unit.id] = {
            'unit_id': str(unit.id),
            'order_type': 'move',
            'origin': unit.territory.abbreviation,
            'destination': destination,
            'coast': coast,
            'via_convoy': via_convoy
        }

    def move_displaced(self, unit, destination, coast=''):
        self.request_data['orders'][unit.id] = {
            'unit_id': str(unit.id),
            'order_type': 'move',
            'origin': unit.retreating_from.abbreviation,
            'destination': destination,
            'coast': coast,
        }

    def support(self, unit, aux_unit, aux_destination):
        aux_order_type = (
            'move' if aux_destination != aux_unit.territory.abbreviation
            else 'hold'
        )
        self.request_data['orders'][unit.id] = {
            'unit_id': str(unit.id),
            'order_type': 'support',
            'origin': unit.territory.abbreviation,
            'destination': unit.territory.abbreviation,
            'coast': unit.coast,
            'aux_unit_id': str(aux_unit.id),
            'aux_order_type': aux_order_type,
            'aux_origin': aux_unit.territory.abbreviation,
            'aux_destination': aux_destination
        }

    def create_convoy_route(self, unit, destination, coast='', convoyers=[]):
        self.move(unit, destination, coast, via_convoy=True)
        route = []
        for convoyer in convoyers:
            self.request_data['orders'][convoyer.id] = {
                'unit_id': str(convoyer.id),
                'order_type': 'convoy',
                'origin': convoyer.territory.abbreviation,
                'destination': convoyer.territory.abbreviation,
                'coast': '',
                'aux_unit_id': str(unit.id),
                'aux_order_type': 'move',
                'aux_origin': unit.territory.abbreviation,
                'aux_destination': destination
            }
            route.append({
                'id': str(convoyer.id),
                'unit_type': convoyer.unit_type,
                'coast': convoyer.coast,
                'territory': convoyer.territory.abbreviation,
                'country': convoyer.country,
                'retreating_from': convoyer.retreating_from,
                'invaded_from': convoyer.invaded_from
            })
        self.request_data['convoy_routes'].append({
            'unit_id': str(unit.id),
            'origin': unit.territory.abbreviation,
            'destination': destination,
            'route': route
        })

    def delete(self, unit):
        self.request_data['orders'][unit.id] = {
            'unit_id': str(unit.id),
            'order_type': 'delete',
            'origin': unit.retreating_from.abbreviation,
        }

    def assertUnitInTerritory(self, unit, territory, coast=None):
        new_unit = self.get_unit(unit.id)
        self.assertEqual(new_unit.territory, self.get_terr(territory))
        if coast:
            self.assertEqual(new_unit.coast, coast)

    def assertUnitIsDisplaced(self, unit):
        new_unit = self.get_unit(unit.id)
        self.assertEqual(new_unit.territory, None)
        self.assertTrue(new_unit.active)

    def assertUnitIsInactive(self, unit):
        new_unit = self.get_unit(unit.id)
        self.assertFalse(new_unit.active)
        self.assertIsNone(new_unit.territory)

    def assertCurrentTurn(self, year, season, phase):
        current_turn = self.game.current_turn()
        self.assertEqual(current_turn.year, year)
        self.assertEqual(current_turn.season, season)
        self.assertEqual(current_turn.phase, phase)
