# describe the process of going from a python object to json
from rest_framework import serializers

from .models import (
    GameSession,
    GameSessionStats,
    GermanWord,
    Sentence,
    Translation,
    UserStatistics,
)


class SentenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sentence
        fields = ["id", "sentence", "german_word"]


class TranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Translation
        fields = ["id", "translation", "german_word"]


class GermanWordSerializer(serializers.ModelSerializer):
    sentences = SentenceSerializer(many=True, read_only=True)
    translations = TranslationSerializer(many=True, read_only=True)

    class Meta:
        model = GermanWord
        fields = ["id", "word", "article", "word_type", "sentences", "translations"]


class SentenceResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sentence
        fields = ["sentence"]  # Only include the sentence field


class TranslationResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Translation
        fields = ["translation"]  # Only include the translation field


class GermanWordResponseSerializer(serializers.ModelSerializer):
    sentences = SentenceResponseSerializer(
        many=True, read_only=True
    )  # Use the updated SentenceSerializer
    translations = TranslationResponseSerializer(
        many=True, read_only=True
    )  # Use the updated TranslationSerializer

    class Meta:
        model = GermanWord
        fields = ["id", "word", "article", "word_type", "sentences", "translations"]


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


class GameSessionSerializer(serializers.ModelSerializer):
    green_cards = GermanWordResponseSerializer(many=True)
    yellow_cards = GermanWordResponseSerializer(many=True)
    red_cards = GermanWordResponseSerializer(many=True)
    unclassified_cards = GermanWordResponseSerializer(many=True)
    stats = GameSessionStatsSerializer()

    class Meta:
        model = GameSession
        fields = (
            "green_cards",
            "yellow_cards",
            "red_cards",
            "unclassified_cards",
            "id",
            "stats",
        )


class GameSessionRequestSerializer(serializers.Serializer):
    level = serializers.IntegerField()
    user_id = serializers.IntegerField()
