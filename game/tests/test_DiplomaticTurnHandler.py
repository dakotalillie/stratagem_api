from game import models
from game.lib.ObjectsFromDatabase import ObjectsFromDatabase
from game.lib.StratagemTestCase import StratagemTestCase
from game.lib.turn_handlers.DiplomaticTurnHandler import DiplomaticTurnHandler

import pdb


class SimpleConvoysTestCase(StratagemTestCase):

    def setUp(self):
        super().setUp()
        self.lvp = self.create_unit('Lvp', 'army', 'England')
        self.iri = self.create_unit('IRI', 'fleet', 'England')
        self.mao = self.create_unit('MAO', 'fleet', 'England')
        self.create_convoy_route(self.lvp, 'Spa', 'NC',
                                 convoyers=[self.iri, self.mao])
        self.handler = DiplomaticTurnHandler(self.game, self.request_data)

    def test_correctly_processes_turn(self):
        self.handler.process_turn()
        self.assertUnitInTerritory(self.lvp, 'Spa')
        self.assertUnitInTerritory(self.iri, 'IRI')
        self.assertUnitInTerritory(self.mao, 'MAO')
        self.assertUnitCoast(self.lvp, 'NC')


class ComplexConvoysTestCase1(StratagemTestCase):

    def setUp(self):
        super().setUp()
        self.tun = self.create_unit('Tun', 'army', 'France')
        self.tys = self.create_unit('TYS', 'fleet', 'France')
        self.nap = self.create_unit('Nap', 'fleet', 'Italy')
        self.ion = self.create_unit('ION', 'fleet', 'Italy')
        self.create_convoy_route(self.tun, 'Nap', convoyers=[self.tys])
        self.move(self.ion, 'TYS')
        self.support(self.nap, self.ion, 'move', 'TYS')
        self.handler = DiplomaticTurnHandler(self.game, self.request_data)

    def test_correctly_processes_turn(self):
        self.handler.process_turn()
        self.assertUnitIsDisplaced(self.tys)
        self.assertUnitInTerritory(self.ion, 'TYS')
        self.assertUnitInTerritory(self.tun, 'Tun')
        self.assertUnitInTerritory(self.nap, 'Nap')
