from game.models import Country, Unit, Territory


def standard(game, country_data):
    for country_name, data in country_data.items():
        country = Country.objects.get(name=country_name, game=game)
        for unit in data['startingUnits']:
            territory = Territory.objects.get(
                abbreviation=unit['territory'],
                game=game
            )
            Unit.objects.create(
                unit_type=unit['type'],
                country=country,
                territory=territory,
                coast=unit['coast'],
                game=game
            )


def test_convoys(game):
    england = Country.objects.get(name='England', game=game)
    france = Country.objects.get(name='France', game=game)

    lvp = Territory.objects.get(abbreviation='Lvp', game=game)
    mar = Territory.objects.get(abbreviation='Mar', game=game)
    iri = Territory.objects.get(abbreviation='IRI', game=game)
    mao = Territory.objects.get(abbreviation='MAO', game=game)

    Unit.objects.create(
        unit_type='army',
        country=england,
        territory=lvp,
        game=game
    )
    Unit.objects.create(
        unit_type='fleet',
        country=england,
        territory=iri,
        game=game
    )
    Unit.objects.create(
        unit_type='fleet',
        country=england,
        territory=mao,
        game=game
    )
    Unit.objects.create(
        unit_type='army',
        country=france,
        territory=mar,
        game=game
    )


def test_unit_deletion(game):
    germany = Country.objects.get(name='Germany', game=game)

    ber = Territory.objects.get(abbreviation='Ber', game=game)
    mun = Territory.objects.get(abbreviation='Mun', game=game)
    pru = Territory.objects.get(abbreviation='Pru', game=game)
    ruh = Territory.objects.get(abbreviation='Ruh', game=game)
    kie = Territory.objects.get(abbreviation='Kie', game=game)

    Unit.objects.create(
        unit_type='army',
        country=germany,
        territory=ber,
        game=game
    )
    Unit.objects.create(
        unit_type='army',
        country=germany,
        territory=mun,
        game=game
    )
    Unit.objects.create(
        unit_type='army',
        country=germany,
        territory=pru,
        game=game
    )
    Unit.objects.create(
        unit_type='army',
        country=germany,
        territory=ruh,
        game=game
    )
    Unit.objects.create(
        unit_type='fleet',
        country=germany,
        territory=kie,
        game=game
    )


def ex_12(game):
    austria = Country.objects.get(name='Austria', game=game)
    germany = Country.objects.get(name='Germany', game=game)
    russia = Country.objects.get(name='Russia', game=game)

    ber = Territory.objects.get(abbreviation='Ber', game=game)
    mun = Territory.objects.get(abbreviation='Mun', game=game)
    pru = Territory.objects.get(abbreviation='Pru', game=game)
    war = Territory.objects.get(abbreviation='War', game=game)
    boh = Territory.objects.get(abbreviation='Boh', game=game)
    tyr = Territory.objects.get(abbreviation='Tyr', game=game)

    Unit.objects.create(
        unit_type='army',
        country=austria,
        territory=boh,
        game=game
    )
    Unit.objects.create(
        unit_type='army',
        country=austria,
        territory=tyr,
        game=game
    )
    Unit.objects.create(
        unit_type='army',
        country=germany,
        territory=ber,
        game=game
    )
    Unit.objects.create(
        unit_type='army',
        country=germany,
        territory=mun,
        game=game
    )
    Unit.objects.create(
        unit_type='army',
        country=russia,
        territory=pru,
        game=game
    )
    Unit.objects.create(
        unit_type='army',
        country=russia,
        territory=war,
        game=game
    )


def ex_14(game):
    russia = Country.objects.get(name='Russia', game=game)
    turkey = Country.objects.get(name='Turkey', game=game)

    sev = Territory.objects.get(abbreviation='Sev', game=game)
    rum = Territory.objects.get(abbreviation='Rum', game=game)
    ser = Territory.objects.get(abbreviation='Ser', game=game)
    gre = Territory.objects.get(abbreviation='Gre', game=game)
    bul = Territory.objects.get(abbreviation='Bul', game=game)
    bla = Territory.objects.get(abbreviation='BLA', game=game)

    Unit.objects.create(
        unit_type='army',
        country=russia,
        territory=sev,
        game=game
    )
    Unit.objects.create(
        unit_type='army',
        country=russia,
        territory=rum,
        game=game
    )
    Unit.objects.create(
        unit_type='army',
        country=russia,
        territory=ser,
        game=game
    )
    Unit.objects.create(
        unit_type='army',
        country=russia,
        territory=gre,
        game=game
    )
    Unit.objects.create(
        unit_type='army',
        country=turkey,
        territory=bul,
        game=game
    )
    Unit.objects.create(
        unit_type='fleet',
        country=turkey,
        territory=bla,
        game=game
    )


def ex_25(game):
    austria = Country.objects.get(name='Austria', game=game)
    germany = Country.objects.get(name='Germany', game=game)

    ruh = Territory.objects.get(abbreviation='Ruh', game=game)
    sil = Territory.objects.get(abbreviation='Sil', game=game)
    mun = Territory.objects.get(abbreviation='Mun', game=game)
    boh = Territory.objects.get(abbreviation='Boh', game=game)
    tyr = Territory.objects.get(abbreviation='Tyr', game=game)

    Unit.objects.create(
        unit_type='army',
        country=germany,
        territory=ruh,
        game=game
    )
    Unit.objects.create(
        unit_type='army',
        country=germany,
        territory=sil,
        game=game
    )
    Unit.objects.create(
        unit_type='army',
        country=germany,
        territory=mun,
        game=game
    )
    Unit.objects.create(
        unit_type='army',
        country=austria,
        territory=boh,
        game=game
    )
    Unit.objects.create(
        unit_type='army',
        country=austria,
        territory=tyr,
        game=game
    )


def ex_26(game):
    england = Country.objects.get(name='England', game=game)
    russia = Country.objects.get(name='Russia', game=game)

    nth = Territory.objects.get(abbreviation='NTH', game=game)
    hel = Territory.objects.get(abbreviation='HEL', game=game)
    den = Territory.objects.get(abbreviation='Den', game=game)
    ska = Territory.objects.get(abbreviation='SKA', game=game)
    bal = Territory.objects.get(abbreviation='BAL', game=game)
    ber = Territory.objects.get(abbreviation='Ber', game=game)

    Unit.objects.create(
        unit_type='fleet',
        country=england,
        territory=nth,
        game=game
    )
    Unit.objects.create(
        unit_type='fleet',
        country=england,
        territory=hel,
        game=game
    )
    Unit.objects.create(
        unit_type='fleet',
        country=england,
        territory=den,
        game=game
    )
    Unit.objects.create(
        unit_type='fleet',
        country=russia,
        territory=ska,
        game=game
    )
    Unit.objects.create(
        unit_type='fleet',
        country=russia,
        territory=bal,
        game=game
    )
    Unit.objects.create(
        unit_type='army',
        country=russia,
        territory=ber,
        game=game
    )


def ex_28(game):
    england = Country.objects.get(name='England', game=game)
    france = Country.objects.get(name='France', game=game)

    lon = Territory.objects.get(abbreviation='Lon', game=game)
    nth = Territory.objects.get(abbreviation='NTH', game=game)
    bel = Territory.objects.get(abbreviation='Bel', game=game)
    eng = Territory.objects.get(abbreviation='ENG', game=game)

    Unit.objects.create(
        unit_type='army',
        country=england,
        territory=lon,
        game=game
    )
    Unit.objects.create(
        unit_type='fleet',
        country=england,
        territory=nth,
        game=game
    )
    Unit.objects.create(
        unit_type='army',
        country=france,
        territory=bel,
        game=game
    )
    Unit.objects.create(
        unit_type='fleet',
        country=france,
        territory=eng,
        game=game
    )


def ex_32(game):
    france = Country.objects.get(name='France', game=game)
    italy = Country.objects.get(name='Italy', game=game)

    tun = Territory.objects.get(abbreviation='Tun', game=game)
    tys = Territory.objects.get(abbreviation='TYS', game=game)
    ion = Territory.objects.get(abbreviation='ION', game=game)
    rom = Territory.objects.get(abbreviation='Rom', game=game)
    nap = Territory.objects.get(abbreviation='Nap', game=game)
    apu = Territory.objects.get(abbreviation='Apu', game=game)

    Unit.objects.create(
        unit_type='army',
        country=france,
        territory=tun,
        game=game
    )
    Unit.objects.create(
        unit_type='fleet',
        country=france,
        territory=tys,
        game=game
    )
    Unit.objects.create(
        unit_type='fleet',
        country=france,
        territory=ion,
        game=game
    )
    Unit.objects.create(
        unit_type='army',
        country=france,
        territory=apu,
        game=game
    )
    Unit.objects.create(
        unit_type='fleet',
        country=italy,
        territory=nap,
        game=game
    )
    Unit.objects.create(
        unit_type='fleet',
        country=italy,
        territory=rom,
        game=game
    )
