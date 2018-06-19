import pdb
from django.test import TestCase
from game import constants, models


class GameTestCase(TestCase):

    def setUp(self):
        self.player = models.Player(first_name="Dakota", last_name="Lillie",
                                    email="bewguy101@gmail.com")
        self.player.set_password("helloworld")
        self.player.save()

        country_players = {country: self.player for country in
                           constants.COUNTRIES.as_list()}

        self.game = models.Game(title="New Game")
        self.game.save(country_players=country_players)

    def test_creating_game_instantiates_turn(self):
        turn = models.Turn.objects.get(game=self.game, year=1901,
                                       season="spring", phase="diplomatic")
        self.assertEqual(self.game.current_turn(), turn)

    def test_creating_game_instantiates_countries(self):
        self.assertEqual(len(self.game.countries.all()), 7)

    def test_creating_game_instantiates_countries_with_players(self):
        self.assertEqual(self.game.countries.first().user, self.player)

    def test_creating_game_instantiates_territories(self):
        self.assertEqual(len(self.game.territories.all()), 75)
