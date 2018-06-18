from django.test import TestCase
from game import models


class StratagemTestCase(TestCase):

    def create_unit(self, terr_abbr, unit_type, country_name):
        return self.game.units.create(
            territory=self.get_terr(terr_abbr),
            unit_type=unit_type,
            country=self.game.countries.get(name=country_name)
        )

    def get_unit(self, terr_abbr):
        territory = self.get_terr(terr_abbr)
        return self.game.units.get(territory=territory)

    def get_terr(self, terr_abbr):
        return self.game.territories.get(abbreviation=terr_abbr)

    def hold(self, unit):
        self.request_data['orders'][unit.id] = {
            'unit_id': unit.id,
            'order_type': 'hold',
            'origin': unit.territory.abbreviation,
            'destination': unit.territory.abbreviation,
            'coast': unit.coast
        }

    def move(self, unit, destination, coast='', via_convoy=False):
        self.request_data['orders'][unit.id] = {
            'unit_id': unit.id,
            'order_type': 'move',
            'origin': unit.territory.abbreviation,
            'destination': destination,
            'coast': coast,
            'via_convoy': via_convoy
        }

    def move_displaced(self, unit, destination, coast=''):
        self.request_data['orders'][unit.id] = {
            'unit_id': unit.id,
            'order_type': 'move',
            'origin': unit.retreating_from.abbreviation,
            'destination': destination,
            'coast': coast,
        }

    def support(self, unit, aux_unit, aux_order_type, aux_destination):
        self.request_data['orders'][unit.id] = {
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

    def create_convoy_route(self, aux_unit, aux_destination, aux_coast='',
                            units=[]):
        self.move(aux_unit, aux_destination, aux_coast, via_convoy=True)
        route = []
        for unit in units:
            self.request_data['orders'][unit.id] = {
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
            route.append({
                'id': unit.id,
                'unit_type': unit.unit_type,
                'coast': unit.coast,
                'territory': unit.territory.abbreviation,
                'country': unit.country,
                'retreating_from': unit.retreating_from,
                'invaded_from': unit.invaded_from
            })
        self.request_data['convoy_routes'].append({
            'unit_id': aux_unit.id,
            'origin': aux_unit.territory.abbreviation,
            'destination': aux_destination,
            'route': route
        })
