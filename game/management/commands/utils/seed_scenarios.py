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
