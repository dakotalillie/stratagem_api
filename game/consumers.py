from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json

from . import serializers
from . import utils
from . import models


class GameConsumer(WebsocketConsumer):

    def connect(self):
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.game_group_name = f'game_{self.game_id}'

        # Join game group
        async_to_sync(self.channel_layer.group_add)(
            self.game_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave game group
        async_to_sync(self.channel_layer.group_discard)(
            self.game_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        unformatted_data = json.loads(text_data)
        data = utils.dict_keys_to_snake_case(unformatted_data)
        types = {
            'submit_orders': self.submit_orders
        }
        types[data['type']](data['payload'])

    def submit_orders(self, payload):
        self.user = (
            self.user if hasattr(self, 'user')
            else models.Player.objects.get(pk=payload['user_id'])
        )
        game = models.Game.objects.get(pk=self.game_id)
        countries = game.countries.all()

        self._mark_player_countries_as_ready(countries)
        if all(country.ready for country in countries):
            turn_processor = utils.get_turn_processor(game, payload)
            turn_processor.process_turn()
            serializer = serializers.GameDetailSerializer(game)
            async_to_sync(self.channel_layer.group_send)(
                self.game_group_name,
                {
                    'type': 'game_data',
                    'payload': serializer.data
                }
            )

    def game_data(self, event):
        self.send(text_data=json.dumps(event['payload']))

    def _mark_player_countries_as_ready(self, countries):
        for country in countries:
            if country.user == self.user:
                country.ready = True
                country.save()
    