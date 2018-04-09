from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Game


class GameSerializer(serializers.ModelSerializer):

    class Meta:
        model = Game
        fields = ('id', 'title')


class UserSerializer(serializers.ModelSerializer):

    games = GameSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email',
                  'first_name', 'last_name', 'games')
