# describe the process of going from a python object to json
from rest_framework import serializers

from .models import (
    GameSessionStats,
    UserStatistics,
)


class GermanWordSerializer(serializers.Serializer):
    """
    Serializer for mongo German word
    """

    translations = serializers.SerializerMethodField()
    _id = serializers.CharField()
    word = serializers.CharField()

    class Meta:
        fields = ["id", "word", "types"]

    def get_translations(self, obj):
        if "types" not in obj:
            return []

        all_translations = []
        for type_entry in obj["types"]:
            all_translations.extend(type_entry.get("translations", []))

        return list(set(t.strip().lower() for t in all_translations))


class UserStatisticSerializer(serializers.ModelSerializer):
    class Meta:
        model: UserStatistics
        fields = "__all__"


class GameSessionStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameSessionStats
        fields = "__all__"


class GameSessionStatsRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameSessionStats
        fields = (
            "total_responses",
            "highest_score",
            "highest_answer_streak",
            "total_time_played",
        )


class GameSessionUpdateRequestSerializer(serializers.Serializer):
    green_cards = serializers.ListField(
        child=serializers.DictField(child=serializers.IntegerField())
    )
    yellow_cards = serializers.ListField(
        child=serializers.DictField(child=serializers.IntegerField())
    )
    red_cards = serializers.ListField(
        child=serializers.DictField(child=serializers.IntegerField())
    )
    stats = GameSessionStatsRequestSerializer()


class GameSessionUpdateResponseSerializer(serializers.Serializer):
    full_green = serializers.BooleanField()
    highest_score = serializers.BooleanField()
    lowest_game_time = serializers.BooleanField()
    new_level = serializers.BooleanField()


class GameSessionResponseSerializer(serializers.Serializer):
    green_cards = serializers.ListField(child=GermanWordSerializer())
    yellow_cards = serializers.ListField(child=GermanWordSerializer())
    red_cards = serializers.ListField(child=GermanWordSerializer())
    unclassified_cards = serializers.ListField(child=GermanWordSerializer())
    id = serializers.IntegerField()


class GameSessionRequestSerializer(serializers.Serializer):
    level = serializers.IntegerField()
    user_id = serializers.IntegerField()
