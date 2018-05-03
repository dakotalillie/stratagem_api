import pdb
from django.test import TestCase
from game import constants, models


class GameTestCase(TestCase):

    def setUp(self):
        player = models.Player(first_name="Dakota", last_name="Lillie",
                               email="bewguy101@gmail.com")
        player.set_password("helloworld")
        player.save()

        country_players = {country: player for country in
                           constants.COUNTRY_NAMES}

        game = models.Game(title="New Game")
        game.save(country_players=country_players)

    def test_creating_game_instantiates_turn(self):
        game = models.Game.objects.get(title="New Game")
        turn = models.Turn.objects.get(game=game, year=1901, season="spring",
                                       phase="diplomatic")
        self.assertEqual(game.current_turn(), turn)

    def test_creating_game_instantiates_countries(self):
        game = models.Game.objects.get(title="New Game")
        self.assertEqual(len(game.countries.all()), 7)
