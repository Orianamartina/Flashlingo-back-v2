import json
from datetime import timedelta

from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .exceptions import GameBlockedException
from .models import GameSession, GameSessionStats, GermanWord, UserStatistics
from .serializers import (
    GameSessionSerializer,
    GameSessionStatsSerializer,
    GameSessionUpdateRequestSerializer,
    GermanWordSerializer,
)
from .utils import get_words_for_game_session


# Create your views here. endpoints
class GermanWordsView(APIView):
    """
    Get all words
    """

    permission_classes = []

    @extend_schema(
        request=None,
        responses={200: GermanWordSerializer(many=True)},
        description="Retrieve a list of all German words",
    )
    def get(self, request, *kwargs):
        all_words = GermanWord.objects.all()
        serializer = GermanWordSerializer(all_words, many=True)
        return Response(serializer.data)


class GermanWordsByIdView(APIView):
    """
    Obtain a word by it's id
    """

    @extend_schema(
        responses={200: GermanWordSerializer, 404: {"error": "Word not found"}},
        description="Retrieve a German word by its ID",
    )
    def get(self, request, id, *kwargs):
        try:
            found_word = GermanWord.objects.get(pk=id)
        except GermanWord.DoesNotExist:
            return Response(
                {"error": "Word not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = GermanWordSerializer(found_word)
        return Response(serializer.data)


class GetGameSessionView(APIView):
    """
    Obtain a game session
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Game Session"],
        summary="Get or create a game session",
        description="Retrieve an existing game session or create a new one if it doesn't exist for the given user and level.",
        responses={
            200: GameSessionSerializer,
            201: GameSessionSerializer,
            400: OpenApiResponse(
                description="Game session is blocked",
                examples=[{"error": "Game session is currently blocked."}],
            ),
            401: OpenApiResponse(
                description="Unauthorized access. Please provide valid credentials."
            ),
        },
        parameters=[
            OpenApiParameter(
                name="level",
                description="Level of the game session",
                required=True,
                type=int,
            )
        ],
    )
    def get(self, request, id, *kwargs):
        try:
            game_session = GameSession.objects.get(id=id)
            print(game_session)
            if game_session.stats.blocked:
                raise GameBlockedException()
            if game_session.isEmpty:
                german_words = get_words_for_game_session(game_session.level)
                game_session.unclassified_cards.set(german_words)
                game_session.isEmpty = False
                game_session.save()

            serializer = GameSessionSerializer(game_session)

            return JsonResponse(serializer.data)
        except GameBlockedException as e:
            return JsonResponse({"error": str(e)}, status=400)

        except Exception as e:
            return JsonResponse({"error": e})


class UpdateGameSessionView(APIView):
    """
    Updates game session
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="update_game_session",
        summary="Update a Game Session",
        description="Updates the game session by clearing and re-assigning card classifications.",
        parameters=[
            OpenApiParameter(
                name="session_id",
                description="ID of the game session",
                required=True,
                type=int,
            )
        ],
        request=GameSessionUpdateRequestSerializer,
        responses={
            200: inline_serializer(
                name="GameSessionUpdateResponse",
                fields={"success": serializers.CharField()},
            ),
            404: inline_serializer(
                name="GameSessionUpdateNotFoundResponse",
                fields={"error": serializers.CharField()},
            ),
            400: inline_serializer(
                name="GameSessionUpdateErrorResponse",
                fields={"error": serializers.CharField()},
            ),
        },
    )
    def post(self, request, session_id, *kwargs):
        response = {
            "full_green": False,
            "highest_score": False,
            "lowest_game_time": False,
            "new_level": False,
        }
        try:
            with transaction.atomic():

                game_session = GameSession.objects.get(id=session_id)
                if game_session.user != request.user:
                    raise Exception("Unauthorized user")

                data = json.loads(request.body)
                # Clear the existing cards
                game_session.red_cards.clear()
                game_session.yellow_cards.clear()
                game_session.green_cards.clear()
                game_session.unclassified_cards.clear()

                # Check if the number of cards is valid
                if (
                    len(data["green_cards"])
                    + len(data["yellow_cards"])
                    + len(data["red_cards"])
                ) != 50:
                    raise Exception("Invalid number of cards")

                empty_cards = 0
                session_words = {
                    "green_cards": data["green_cards"],
                    "red_cards": data["red_cards"],
                    "yellow_cards": data["yellow_cards"],
                }
                print("parsing cards")
                for classification, words in session_words.items():
                    print(classification)
                    if len(words) == 0:
                        empty_cards += 1
                    for word in words:
                        german_word = GermanWord.objects.get(id=word)

                        if classification == "green_cards":
                            game_session.green_cards.add(german_word)
                        elif classification == "yellow_cards":
                            game_session.yellow_cards.add(german_word)
                        elif classification == "red_cards":
                            game_session.red_cards.add(german_word)

                if empty_cards == 4:
                    raise Exception("Too many empty card classifications")

                game_session.save()
                # Update the stats
                game_stats = game_session.stats
                new_stats = GameSessionStatsSerializer(data=data["stats"])
                if new_stats.is_valid():
                    new_stats_data = new_stats.validated_data

                    game_stats.green_cards = len(data["green_cards"])
                    if game_stats.green_cards == 50:
                        response["full_green"] = True
                    game_stats.yellow_cards = len(data["yellow_cards"])
                    game_stats.red_cards = len(data["red_cards"])
                    game_stats.total_time_played += new_stats_data["total_time_played"]
                    game_stats.score += new_stats_data["score"]
                    if (
                        game_stats.lowest_game_time == 0
                        or game_stats.lowest_game_time
                        > new_stats_data["total_time_played"]
                    ):
                        game_stats.lowest_game_time = new_stats_data[
                            "total_time_played"
                        ]
                        response["lowest_game_time"] = True

                    game_stats.total_responses += new_stats_data["total_responses"]
                    if game_stats.highest_score < new_stats_data["highest_score"]:
                        response["highest_score"] = True
                    game_stats.highest_score = max(
                        game_stats.highest_score, new_stats_data["highest_score"]
                    )
                    game_stats.highest_answer_streak = max(
                        game_stats.highest_answer_streak,
                        new_stats_data["highest_answer_streak"],
                    )
                    game_stats.save()

                # Check for user level progress
                user_stats = UserStatistics.objects.get(user=request.user)
                if (
                    game_stats.level == user_stats.highest_level
                    and game_stats.points >= 70
                ):
                    user_stats.highest_level += 1
                    user_stats.save()
                    next_level = GameSessionStats.objects.get(
                        level=game_stats.level + 1, user=request.user
                    )
                    next_level.unlock()
                    next_level.save()
                    response["new_level"] = True

                today = timezone.now().date()
                stats = UserStatistics.objects.get(user=request.user)

                if stats.last_day_played == today - timedelta(days=1):
                    stats.days_streak += 1
                if stats.days_streak > stats.longest_streak:
                    stats.longest_streak = stats.days_streak
                else:
                    stats.days_streak = 1

                stats.last_day_played = today
                stats.save()

                return JsonResponse(response, status=200)

        except UserStatistics.DoesNotExist:
            today = timezone.now().date()
            stats = UserStatistics.objects.create(
                user=request.user,
                last_day_played=today,
                days_streak=1,
                longest_streak=1,
            )
            return JsonResponse(response, status=200)

        except GameSession.DoesNotExist:
            return JsonResponse({"error": "Game session not found"}, status=404)

        except Exception as e:
            return JsonResponse({"error": f"{e}"}, status=400)


class GetAllSessionStats(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="all_session_stats",
        summary="Get all game session statistics from a user",
        description="Returns a list containing all game session stats of the authenticated user",
        responses={
            200: inline_serializer(
                name="AllSessionStatsResponse",
                fields={"success": GameSessionStatsSerializer()},
            ),
            400: inline_serializer(
                name="AllSesionStatsErrorResponse",
                fields={"error": serializers.CharField()},
            ),
        },
    )
    def get(self, request):
        try:
            game_stats = GameSessionStats.objects.filter(user=request.user)
            serializer = GameSessionStatsSerializer(game_stats, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({"error": f"{e}"}, status=400)
