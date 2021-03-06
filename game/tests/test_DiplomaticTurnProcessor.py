from game.lib import StratagemTestCase
from game.lib.turn_processors import DiplomaticTurnProcessor


class SimpleMoveOrderTestCase(StratagemTestCase):
    """
    Rulebook: page 7, diagrams 1 and 2
    Basic movement.
    """

    def setUp(self):
        super().setUp()
        self.par = self.create_unit('Par', 'army', 'France')
        self.eng = self.create_unit('ENG', 'fleet', 'France')
        self.issue_move_order(self.par, 'Bur')
        self.issue_move_order(self.eng, 'Bel')
        DiplomaticTurnProcessor(self.game, self.request_data).process_turn()

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
        self.issue_move_order(self.ber, 'Sil')
        self.issue_move_order(self.war, 'Sil')
        DiplomaticTurnProcessor(self.game, self.request_data).process_turn()

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
        self.issue_move_order(self.ber, 'Pru')
        self.issue_move_order(self.pru, 'Ber')
        DiplomaticTurnProcessor(self.game, self.request_data).process_turn()

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
        self.issue_move_order(self.mar, 'Bur')
        self.issue_support_order(self.gas, self.mar, 'Bur')
        DiplomaticTurnProcessor(self.game, self.request_data).process_turn()

    def test_correctly_processes_turn(self):
        self.assertUnitIsDisplaced(self.bur)
        self.assertUnitInTerritory(self.mar, 'Bur')


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
        self.issue_support_order(self.ber, self.mun, 'Sil')
        self.issue_move_order(self.mun, 'Sil')
        self.issue_support_order(self.pru, self.war, 'Sil')
        self.issue_move_order(self.war, 'Sil')
        self.issue_support_order(self.tyr, self.boh, 'Mun')
        self.issue_move_order(self.boh, 'Mun')
        DiplomaticTurnProcessor(self.game, self.request_data).process_turn()

    def test_correctly_processes_turn(self):
        self.assertUnitIsDisplaced(self.mun)
        self.assertUnitInTerritory(self.boh, 'Mun')
        self.assertUnitInTerritory(self.war, 'War')


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
        self.issue_move_order(self.sev, 'Rum')
        self.issue_move_order(self.rum, 'Bul')
        self.issue_support_order(self.ser, self.rum, 'Bul')
        self.issue_support_order(self.gre, self.rum, 'Bul')
        self.issue_move_order(self.bul, 'Rum')
        self.issue_support_order(self.bla, self.bul, 'Rum')
        DiplomaticTurnProcessor(self.game, self.request_data).process_turn()

    def test_correctly_processes_turn(self):
        self.assertUnitIsDisplaced(self.bul)
        self.assertUnitInTerritory(self.sev, 'Rum')
        self.assertUnitInTerritory(self.rum, 'Bul')


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
        self.issue_move_order(self.mun, 'Sil')
        self.issue_move_order(self.pru, 'Ber')
        self.issue_support_order(self.sil, self.pru, 'Ber')
        self.issue_move_order(self.boh, 'Mun')
        self.issue_support_order(self.tyr, self.boh, 'Mun')
        DiplomaticTurnProcessor(self.game, self.request_data).process_turn()

    def test_correctly_processes_turn(self):
        self.assertUnitIsDisplaced(self.mun)
        self.assertUnitInTerritory(self.ber, 'Ber')
        self.assertUnitInTerritory(self.pru, 'Pru')
        self.assertUnitInTerritory(self.boh, 'Mun')


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
        DiplomaticTurnProcessor(self.game, self.request_data).process_turn()

    def test_correctly_processes_turn(self):
        self.assertUnitInTerritory(self.lvp, 'Spa', coast='NC')


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
        self.issue_move_order(self.vie, 'Tri')
        self.issue_move_order(self.ser, 'Bud')
        self.issue_support_order(self.tri, self.ser, 'Bud')
        DiplomaticTurnProcessor(self.game, self.request_data).process_turn()

    def test_correctly_processes_turn(self):
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
        DiplomaticTurnProcessor(self.game, self.request_data).process_turn()

    def test_correctly_processes_turn(self):
        self.assertUnitInTerritory(self.lon, 'Bel')
        self.assertUnitInTerritory(self.bel, 'Lon')


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
        self.issue_move_order(self.bre, 'ENG')
        self.issue_support_order(self.iri, self.bre, 'ENG')
        DiplomaticTurnProcessor(self.game, self.request_data).process_turn()

    def test_correctly_processes_turn(self):
        self.assertUnitIsDisplaced(self.eng)
        self.assertUnitInTerritory(self.bre, 'ENG')
        self.assertUnitInTerritory(self.lon, 'Bel')


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
        self.issue_move_order(self.ion, 'TYS')
        self.issue_support_order(self.nap, self.ion, 'TYS')
        DiplomaticTurnProcessor(self.game, self.request_data).process_turn()

    def test_correctly_processes_turn(self):
        self.assertUnitIsDisplaced(self.tys)
        self.assertUnitInTerritory(self.ion, 'TYS')
        self.assertUnitInTerritory(self.tun, 'Tun')


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
        self.issue_move_order(self.rom, 'TYS')
        self.issue_support_order(self.nap, self.rom, 'TYS')
        DiplomaticTurnProcessor(self.game, self.request_data).process_turn()

    def test_correctly_processes_turn(self):
        self.assertUnitInTerritory(self.tys, 'TYS')
        self.assertUnitInTerritory(self.rom, 'Rom')


class UpdateTurnTestCase1(StratagemTestCase):
    """
    If current season is spring and no retreat phase is necessary,
    transitions to fall.
    """

    def setUp(self):
        super().setUp()
        DiplomaticTurnProcessor(self.game, self.request_data).process_turn()

    def test_correctly_processes_turn(self):
        self.assertCurrentTurn(1901, 'fall', 'diplomatic')


class UpdateTurnTestCase2(StratagemTestCase):
    """
    If a retreat phase is necessary, transitions to retreat phase of
    the same season.
    """

    def setUp(self):
        super().setUp()
        self.mar = self.create_unit('Mar', 'army', 'France')
        self.gas = self.create_unit('Gas', 'army', 'France')
        self.bur = self.create_unit('Bur', 'army', 'Germany')
        self.issue_move_order(self.mar, 'Bur')
        self.issue_support_order(self.gas, self.mar, 'Bur')
        DiplomaticTurnProcessor(self.game, self.request_data).process_turn()

    def test_correctly_processes_turn(self):
        self.assertCurrentTurn(1901, 'spring', 'retreat')


class UpdateTurnTestCase3(StratagemTestCase):
    """
    If the current season is fall and no retreat phase is necessary,
    transitions to fall reinforcement phase.
    """

    def setUp(self):
        super().setUp()
        self.set_current_turn(1901, 'fall', 'diplomatic')
        DiplomaticTurnProcessor(self.game, self.request_data).process_turn()

    def test_correctly_processes_turn(self):
        self.assertCurrentTurn(1901, 'fall', 'reinforcement')
