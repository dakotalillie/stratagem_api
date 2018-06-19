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


class CuttingSupportOnOwnUnitsTestCase(StratagemTestCase):
    """
    Rulebook: page 16
    An attack by a country on one of its own units doesn't cut support
    """

    def setUp(self):
        super().setUp()
        self.vie = self.create_unit('Vie', 'army', 'Austria')
        self.tri = self.create_unit('Tri', 'army', 'Austria')
        self.ser = self.create_unit('Ser', 'army', 'Austria')
        self.bud = self.create_unit('Bud', 'army', 'Russia')
        self.move(self.vie, 'Tri')
        self.move(self.ser, 'Bud')
        self.support(self.tri, self.ser, 'move', 'Bud')
        self.handler = DiplomaticTurnHandler(self.game, self.request_data)

    def test_correctly_processes_turn(self):
        self.handler.process_turn()
        self.assertUnitInTerritory(self.vie, 'Vie')
        self.assertUnitInTerritory(self.tri, 'Tri')
        self.assertUnitInTerritory(self.ser, 'Bud')
        self.assertUnitIsDisplaced(self.bud)


class ExchangePlacesViaConvoyTestCase(StratagemTestCase):
    """
    Rulebook: diagram 28, page 16
    Two units can exchange places if either or both are convoyed.
    """

    def setUp(self):
        super().setUp()
        self.lon = self.create_unit('Lon', 'army', 'England')
        self.nth = self.create_unit('NTH', 'fleet', 'England')
        self.bel = self.create_unit('Bel', 'army', 'France')
        self.eng = self.create_unit('ENG', 'fleet', 'France')
        self.create_convoy_route(self.lon, 'Bel', convoyers=[self.nth])
        self.create_convoy_route(self.bel, 'Lon', convoyers=[self.eng])
        self.handler = DiplomaticTurnHandler(self.game, self.request_data)

    def test_correctly_processes_turn(self):
        self.handler.process_turn()
        self.assertUnitInTerritory(self.lon, 'Bel')
        self.assertUnitInTerritory(self.bel, 'Lon')
        self.assertUnitInTerritory(self.eng, 'ENG')
        self.assertUnitInTerritory(self.nth, 'NTH')


class MultipleConvoyRoutesTestCase(StratagemTestCase):
    """
    Rulebook: diagram 29, page 16
    An army convoyed using alternate convoy orders reaches its
    destination as long as at least one convoy route remains open.
    """

    def setUp(self):
        super().setUp()
        self.lon = self.create_unit('Lon', 'army', 'England')
        self.eng = self.create_unit('ENG', 'fleet', 'England')
        self.nth = self.create_unit('NTH', 'fleet', 'England')
        self.bre = self.create_unit('Bre', 'fleet', 'France')
        self.iri = self.create_unit('IRI', 'fleet', 'France')
        self.create_convoy_route(self.lon, 'Bel', convoyers=[self.eng])
        self.create_convoy_route(self.lon, 'Bel', convoyers=[self.nth])
        self.move(self.bre, 'ENG')
        self.support(self.iri, self.bre, 'move', 'ENG')
        self.handler = DiplomaticTurnHandler(self.game, self.request_data)

    def test_correctly_processes_turn(self):
        self.handler.process_turn()
        self.assertUnitIsDisplaced(self.eng)
        self.assertUnitInTerritory(self.lon, 'Bel')
        self.assertUnitInTerritory(self.bre, 'ENG')
        self.assertUnitInTerritory(self.iri, 'IRI')
        self.assertUnitInTerritory(self.nth, 'NTH')


class ComplexConvoysTestCase1(StratagemTestCase):
    """
    Rulebook: diagram 30, page 17
    A convoyed army doesn't cut the support of a unit supporting an
    attack against one of the fleets necessary for the army to convoy
    (unless there exists an alternative, successful route)
    """

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


class ComplexConvoysTestCase2(StratagemTestCase):
    """
    Rulebook: diagram 31, page 17
    An army with at least one successful convoy route will cut the
    support given by a unit in the destination territory that is trying
    to support an attack on a fleet in an alternate route route of that
    convoy.
    """

    def setUp(self):
        super().setUp()
        self.tun = self.create_unit('Tun', 'army', 'France')
        self.tys = self.create_unit('TYS', 'fleet', 'France')
        self.ion = self.create_unit('ION', 'fleet', 'France')
        self.nap = self.create_unit('Nap', 'fleet', 'Italy')
        self.rom = self.create_unit('Rom', 'fleet', 'Italy')
        self.create_convoy_route(self.tun, 'Nap', convoyers=[self.tys])
        self.create_convoy_route(self.tun, 'Nap', convoyers=[self.ion])
        self.move(self.rom, 'TYS')
        self.support(self.nap, self.rom, 'move', 'TYS')
        self.handler = DiplomaticTurnHandler(self.game, self.request_data)

    def test_correctly_processes_turn(self):
        self.handler.process_turn()
        self.assertUnitInTerritory(self.tun, 'Tun')
        self.assertUnitInTerritory(self.tys, 'TYS')
        self.assertUnitInTerritory(self.ion, 'ION')
        self.assertUnitInTerritory(self.nap, 'Nap')
        self.assertUnitInTerritory(self.rom, 'Rom')
