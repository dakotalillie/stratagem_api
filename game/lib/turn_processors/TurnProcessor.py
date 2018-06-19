import json
from abc import ABC

from game.models import Order
from game.lib import ObjectsFromDatabase


class TurnProcessor(ABC):

    def __init__(self, game, request_data):
        self.game = game
        self.request_data = request_data
        self.db_objects = ObjectsFromDatabase(game)
        self.retreat_phase_necessary = False
        self.orders = []

    def _create_order_from_data(self, order_data):
        unit = (self.db_objects.units[order_data['unit_id']]
                if 'unit_id' in order_data
                else None)
        destination = (self.db_objects.territories[order_data['destination']]
                       if 'destination' in order_data
                       else None)
        coast = order_data['coast'] if 'coast' in order_data else ''
        unit_type = (order_data['unit_type']
                     if 'unit_type' in order_data
                     else unit.unit_type)
        aux_unit = None
        aux_order_type = ''
        aux_origin = None
        aux_destination = None
        via_convoy = False

        if 'aux_unit_id' in order_data:
            aux_unit = self.db_objects.units[order_data['aux_unit_id']]
            aux_order_type = order_data['aux_order_type']
            aux_origin = self.db_objects.territories[order_data['aux_origin']]
            aux_destination = self.db_objects.territories[
                order_data['aux_destination']
            ]

        if 'via_convoy' in order_data:
            via_convoy = order_data['via_convoy']

        order = Order(
            turn=self.game.current_turn(),
            unit=self.db_objects.units[order_data['unit_id']],
            unit_type=unit_type,
            order_type=order_data['order_type'],
            origin=self.db_objects.territories[order_data['origin']],
            destination=destination,
            coast=coast,
            aux_unit=aux_unit,
            aux_order_type=aux_order_type,
            aux_origin=aux_origin,
            aux_destination=aux_destination,
            via_convoy=via_convoy
        )

        order.save()
        return order

    def _create_default_hold_order(self, unit):
        order = Order(
            turn=self.game.current_turn(),
            unit=unit,
            order_type='hold',
            origin=unit.territory,
            destination=unit.territory,
            coast=unit.coast
        )

        order.save()
        return order

    def _create_default_delete_order(self, unit):
        order = Order(
            turn=self.game.current_turn(),
            unit=unit,
            order_type='delete',
            origin=unit.retreating_from
        )

        order.save()
        return order

    def _update_turn(self):
        self._create_new_turn()
        if self.game.current_turn().phase == 'reinforcement':
            self._update_territory_owners()

    def _create_new_turn(self):
        current_turn = self.game.current_turn()
        if current_turn.phase == 'diplomatic':
            if self.retreat_phase_necessary:
                return self.game.turns.create(
                    year=current_turn.year,
                    season=current_turn.season,
                    phase='retreat'
                )
            elif (not self.retreat_phase_necessary and
                    current_turn.season == 'fall'):
                return self.game.turns.create(
                    year=current_turn.year,
                    season='fall',
                    phase='reinforcement'
                )
            else:
                return self.game.turns.create(
                    year=current_turn.year,
                    season='fall',
                    phase='diplomatic'
                )
        elif current_turn.phase == 'retreat':
            if current_turn.season == 'fall':
                return self.game.turns.create(
                    year=current_turn.year,
                    season='fall',
                    phase='reinforcement'
                )
            else:
                return self.game.turns.create(
                    year=current_turn.year,
                    season='fall',
                    phase='diplomatic'
                )
        elif current_turn.phase == 'reinforcement':
            return self.game.turns.create(
                year=current_turn.year + 1,
                season='spring',
                phase='diplomatic'
            )

    def _update_territory_owners(self):
        with open('game/data/territories.json') as territories_json:
            territory_data = json.loads(territories_json.read())

        for unit in self.game.units.filter(active=True):
            water_terr = (
                territory_data[unit.territory.abbreviation]['type'] == 'water'
            )
            if unit.country != unit.territory.owner and not water_terr:
                unit.territory.owner = unit.country
                unit.territory.save()
