from game import models
from game.lib.ObjectsFromDatabase import ObjectsFromDatabase
from game.lib.StratagemTestCase import StratagemTestCase
from game.lib.turn_handlers.DiplomaticTurnHandler import DiplomaticTurnHandler


class SimpleMoveOrderTestCase(StratagemTestCase):
    """
    Rulebook: page 7, diagrams 1 and 2
    Basic movement.
    """

    def setUp(self):
        super().setUp()
        self.par = self.create_unit('Par', 'army', 'France')
        self.eng = self.create_unit('ENG', 'fleet', 'France')
        self.move(self.par, 'Bur')
        self.move(self.eng, 'Bel')
        DiplomaticTurnHandler(self.game, self.request_data).process_turn()

    def test_correctly_processes_turn(self):
        self.assertUnitInTerritory(self.par, 'Bur')
        self.assertUnitInTerritory(self.eng, 'Bel')


class SimpleStandoffTestCase(StratagemTestCase):
    """
    Rulebook: page 8, diagram 4
    Units of equal strength trying to occupy the same territory cause
    all those units to remain in their original territory.
    """

    def setUp(self):
        super().setUp()
        self.ber = self.create_unit('Ber', 'army', 'Germany')
        self.war = self.create_unit('War', 'army', 'Russia')
        self.move(self.ber, 'Sil')
        self.move(self.war, 'Sil')
        DiplomaticTurnHandler(self.game, self.request_data).process_turn()

    def test_correctly_processes_turn(self):
        self.assertUnitInTerritory(self.ber, 'Ber')
        self.assertUnitInTerritory(self.war, 'War')


class IllegalSwapsTestCase(StratagemTestCase):
    """
    Rulebook: page 9, diagram 6
    Units can't trade places without the use of a convoy.
    """

    def setUp(self):
        super().setUp()
        self.ber = self.create_unit('Ber', 'army', 'Germany')
        self.pru = self.create_unit('Pru', 'army', 'Russia')
        self.move(self.ber, 'Pru')
        self.move(self.pru, 'Ber')
        DiplomaticTurnHandler(self.game, self.request_data).process_turn()

    def test_correctly_processes_turn(self):
        self.assertUnitInTerritory(self.ber, 'Ber')
        self.assertUnitInTerritory(self.pru, 'Pru')


class SimpleSupportTestCase(StratagemTestCase):
    """
    Rulebook: page 10, diagram 8
    Basic support.
    """

    def setUp(self):
        super().setUp()
        self.mar = self.create_unit('Mar', 'army', 'France')
        self.gas = self.create_unit('Gas', 'army', 'France')
        self.bur = self.create_unit('Bur', 'army', 'Germany')
        self.move(self.mar, 'Bur')
        self.support(self.gas, self.mar, 'Bur')
        DiplomaticTurnHandler(self.game, self.request_data).process_turn()

    def test_correctly_processes_turn(self):
        self.assertUnitIsDisplaced(self.bur)
        self.assertUnitInTerritory(self.mar, 'Bur')
        self.assertUnitInTerritory(self.gas, 'Gas')


class ComplexSupportTestCase1(StratagemTestCase):
    """
    Rulebook: page 11, diagram 12
    A dislodged unit can still cause a standoff in a territory different
    from the one that dislodged it.
    """

    def setUp(self):
        super().setUp()
        self.ber = self.create_unit('Ber', 'army', 'Germany')
        self.mun = self.create_unit('Mun', 'army', 'Germany')
        self.pru = self.create_unit('Pru', 'army', 'Russia')
        self.war = self.create_unit('War', 'army', 'Russia')
        self.boh = self.create_unit('Boh', 'army', 'Austria')
        self.tyr = self.create_unit('Tyr', 'army', 'Austria')
        self.support(self.ber, self.mun, 'Sil')
        self.move(self.mun, 'Sil')
        self.support(self.pru, self.war, 'Sil')
        self.move(self.war, 'Sil')
        self.support(self.tyr, self.boh, 'Mun')
        self.move(self.boh, 'Mun')
        DiplomaticTurnHandler(self.game, self.request_data).process_turn()

    def test_correctly_processes_turn(self):
        self.assertUnitIsDisplaced(self.mun)
        self.assertUnitInTerritory(self.boh, 'Mun')
        self.assertUnitInTerritory(self.ber, 'Ber')
        self.assertUnitInTerritory(self.pru, 'Pru')
        self.assertUnitInTerritory(self.war, 'War')
        self.assertUnitInTerritory(self.tyr, 'Tyr')


class ComplexSupportTestCase2(StratagemTestCase):
    """
    Rulebook: page 12, diagram 14
    A dislodged unit, even with support, has no effect on the province
    that dislodged it.
    """

    def setUp(self):
        super().setUp()
        self.sev = self.create_unit('Sev', 'army', 'Russia')
        self.rum = self.create_unit('Rum', 'army', 'Russia')
        self.ser = self.create_unit('Ser', 'army', 'Russia')
        self.gre = self.create_unit('Gre', 'army', 'Russia')
        self.bul = self.create_unit('Bul', 'army', 'Turkey')
        self.bla = self.create_unit('BLA', 'army', 'Turkey')
        self.move(self.sev, 'Rum')
        self.move(self.rum, 'Bul')
        self.support(self.ser, self.rum, 'Bul')
        self.support(self.gre, self.rum, 'Bul')
        self.move(self.bul, 'Rum')
        self.support(self.bla, self.bul, 'Rum')
        DiplomaticTurnHandler(self.game, self.request_data).process_turn()

    def test_correctly_processes_turn(self):
        self.assertUnitIsDisplaced(self.bul)
        self.assertUnitInTerritory(self.sev, 'Rum')
        self.assertUnitInTerritory(self.rum, 'Bul')
        self.assertUnitInTerritory(self.ser, 'Ser')
        self.assertUnitInTerritory(self.gre, 'Gre')
        self.assertUnitInTerritory(self.bla, 'BLA')


class CuttingSupportTestCase(StratagemTestCase):
    """
    Rulebook: page 13, diagram 18
    A unit being dislodged by one territory can still cut support in
    another territory.
    """

    def setUp(self):
        super().setUp()
        self.ber = self.create_unit('Ber', 'army', 'Germany')
        self.mun = self.create_unit('Mun', 'army', 'Germany')
        self.pru = self.create_unit('Pru', 'army', 'Russia')
        self.sil = self.create_unit('Sil', 'army', 'Russia')
        self.boh = self.create_unit('Boh', 'army', 'Austria')
        self.tyr = self.create_unit('Tyr', 'army', 'Austria')
        self.move(self.mun, 'Sil')
        self.move(self.pru, 'Ber')
        self.support(self.sil, self.pru, 'Ber')
        self.move(self.boh, 'Mun')
        self.support(self.tyr, self.boh, 'Mun')
        DiplomaticTurnHandler(self.game, self.request_data).process_turn()

    def test_correctly_processes_turn(self):
        self.assertUnitIsDisplaced(self.mun)
        self.assertUnitInTerritory(self.ber, 'Ber')
        self.assertUnitInTerritory(self.pru, 'Pru')
        self.assertUnitInTerritory(self.sil, 'Sil')
        self.assertUnitInTerritory(self.boh, 'Mun')
        self.assertUnitInTerritory(self.tyr, 'Tyr')


class SimpleConvoysTestCase(StratagemTestCase):
    """
    Rulebook: page 14, diagram 20
    Basic convoy.
    """
    def setUp(self):
        super().setUp()
        self.lvp = self.create_unit('Lvp', 'army', 'England')
        self.iri = self.create_unit('IRI', 'fleet', 'England')
        self.mao = self.create_unit('MAO', 'fleet', 'England')
        self.create_convoy_route(self.lvp, 'Spa', 'NC',
                                 convoyers=[self.iri, self.mao])
        DiplomaticTurnHandler(self.game, self.request_data).process_turn()

    def test_correctly_processes_turn(self):
        self.assertUnitInTerritory(self.lvp, 'Spa', coast='NC')
        self.assertUnitInTerritory(self.iri, 'IRI')
        self.assertUnitInTerritory(self.mao, 'MAO')


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
        self.support(self.tri, self.ser, 'Bud')
        DiplomaticTurnHandler(self.game, self.request_data).process_turn()

    def test_correctly_processes_turn(self):
        self.assertUnitInTerritory(self.vie, 'Vie')
        self.assertUnitInTerritory(self.tri, 'Tri')
        self.assertUnitInTerritory(self.ser, 'Bud')
        self.assertUnitIsDisplaced(self.bud)


class ExchangePlacesViaConvoyTestCase(StratagemTestCase):
    """
    Rulebook: page 16, diagram 28
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
        DiplomaticTurnHandler(self.game, self.request_data).process_turn()

    def test_correctly_processes_turn(self):
        self.assertUnitInTerritory(self.lon, 'Bel')
        self.assertUnitInTerritory(self.bel, 'Lon')
        self.assertUnitInTerritory(self.eng, 'ENG')
        self.assertUnitInTerritory(self.nth, 'NTH')


class MultipleConvoyRoutesTestCase(StratagemTestCase):
    """
    Rulebook: page 16, diagram 29
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
        self.support(self.iri, self.bre, 'ENG')
        DiplomaticTurnHandler(self.game, self.request_data).process_turn()

    def test_correctly_processes_turn(self):
        self.assertUnitIsDisplaced(self.eng)
        self.assertUnitInTerritory(self.lon, 'Bel')
        self.assertUnitInTerritory(self.bre, 'ENG')
        self.assertUnitInTerritory(self.iri, 'IRI')
        self.assertUnitInTerritory(self.nth, 'NTH')


class ComplexConvoysTestCase1(StratagemTestCase):
    """
    Rulebook: page 17, diagram 30
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
        self.support(self.nap, self.ion, 'TYS')
        DiplomaticTurnHandler(self.game, self.request_data).process_turn()

    def test_correctly_processes_turn(self):
        self.assertUnitIsDisplaced(self.tys)
        self.assertUnitInTerritory(self.ion, 'TYS')
        self.assertUnitInTerritory(self.tun, 'Tun')
        self.assertUnitInTerritory(self.nap, 'Nap')


class ComplexConvoysTestCase2(StratagemTestCase):
    """
    Rulebook: page 17, diagram 31
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
        self.support(self.nap, self.rom, 'TYS')
        DiplomaticTurnHandler(self.game, self.request_data).process_turn()

    def test_correctly_processes_turn(self):
        self.assertUnitInTerritory(self.tun, 'Tun')
        self.assertUnitInTerritory(self.tys, 'TYS')
        self.assertUnitInTerritory(self.ion, 'ION')
        self.assertUnitInTerritory(self.nap, 'Nap')
        self.assertUnitInTerritory(self.rom, 'Rom')
