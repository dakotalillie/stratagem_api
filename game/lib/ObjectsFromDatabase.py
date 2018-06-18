class ObjectsFromDatabase():
    """
    Keeping objects from the database in this data structure minimizes
    database calls.
    """

    def __init__(self, game):
        self.game = game
        self.units = {str(u.id): u for u in game.units.filter(active=True)}
        self.territories = {t.abbreviation: t for t in game.territories.all()},
        self.countries = {c.name: c for c in game.countries.all()}