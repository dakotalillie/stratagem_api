from django.test import TestCase
from game import models
from . import diplomatic_utils as du
from . import retreat_utils as rtu


class StratagemTest(TestCase):

    def setUp(self):
        game = models.Game(title="New Game")
        game.save()
        self.objects = {
            'game': game,
            'units': {u.id: u for u in game.units.filter(active=True)},
            'territories': {t.abbreviation: t for t in
                            game.territories.all()},
            'countries': {c.name: c for c in game.countries.all()}
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

    def move_displaced(self, unit, destination, coast=''):
        data = {
            'unit_id': unit.id,
            'order_type': 'move',
            'origin': unit.retreating_from.abbreviation,
            'destination': destination,
            'coast': coast,
        }
        self.orders.append(rtu.create_retreat_order_from_data(data,
                                                              self.objects))

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
