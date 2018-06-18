from django.test import TestCase
from game import models


class StratagemTestCase(TestCase):

    def setUp(self):
        self.game = models.Game(title="New Game")
        self.game.save()
        self.request_data = {'orders': {}, 'convoy_routes': []}

    def create_unit(self, terr_abbr, unit_type, country_name):
        return self.game.units.create(
            territory=self.get_terr(terr_abbr),
            unit_type=unit_type,
            country=self.game.countries.get(name=country_name)
        )

    def get_unit_by_id(self, id):
        return self.game.units.get(pk=id)

    def get_unit_by_terr(self, terr_abbr):
        territory = self.get_terr(terr_abbr)
        return self.game.units.get(territory=territory)

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

    def support(self, unit, aux_unit, aux_order_type, aux_destination):
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

    def assertUnitInTerritory(self, unit, territory):
        new_unit = self.get_unit_by_id(unit.id)
        self.assertEqual(new_unit.territory, self.get_terr(territory))

    def assertUnitCoast(self, unit, coast):
        new_unit = self.get_unit_by_id(unit.id)
        self.assertEqual(new_unit.coast, coast)

    def assertUnitIsDisplaced(self, unit):
        new_unit = self.get_unit_by_id(unit.id)
        self.assertEqual(new_unit.territory, None)
        self.assertTrue(new_unit.active)
