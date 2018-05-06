from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
from .models import Player
from game.serializers import GameOverviewSerializer


class UserSerializer(serializers.ModelSerializer):

    games = GameOverviewSerializer(many=True, read_only=True)

    class Meta:
        model = Player
        fields = ('id', 'username', 'email',
                  'first_name', 'last_name', 'games')


class UserSerializerWithToken(serializers.ModelSerializer):

    token = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True)
    games = GameOverviewSerializer(many=True, read_only=True)

    def get_token(self, obj):
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(obj)
        token = jwt_encode_handler(payload)
        return token

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    class Meta:
        model = Player
        fields = ('token', 'id', 'username', 'email', 'first_name',
                  'last_name', 'password', 'games')