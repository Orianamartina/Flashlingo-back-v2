import json

from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .exceptions import GameBlockedException
from .models import GameSession, GameSessionStats, UserStatistics, word_collection
from .serializers import (
    GameSessionResponseSerializer,
    GameSessionStatsSerializer,
    GameSessionUpdateRequestSerializer,
    GameSessionUpdateResponseSerializer,
)
from .utils import (
    get_words_for_game_session,
    update_game_session,
    update_game_session_stats,
    update_user_stats,
)
import logging

logger = logging.getLogger(__name__)


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
            200: GameSessionResponseSerializer,
            201: GameSessionResponseSerializer,
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
    def get(self, request, stats_id, *kwargs):
        try:
            game_session = GameSession.objects.get(stats_id=stats_id)
            if game_session.stats.blocked:
                raise GameBlockedException()
            if game_session.isEmpty:
                german_words = get_words_for_game_session(game_session.level)

                word_ids = [str(word["_id"]) for word in german_words]

                game_session.unclassified_cards = word_ids
                game_session.isEmpty = False
                game_session.save()

            green_cards = word_collection.find(
                {"_id": {"$in": game_session.green_cards}}
            )
            yellow_cards = word_collection.find(
                {"_id": {"$in": game_session.yellow_cards}}
            )
            red_cards = word_collection.find({"_id": {"$in": game_session.red_cards}})
            unclassified_cards = word_collection.find(
                {"_id": {"$in": game_session.unclassified_cards}}
            )

            serializer_data = {
                "green_cards": green_cards,
                "yellow_cards": yellow_cards,
                "red_cards": red_cards,
                "unclassified_cards": unclassified_cards,
                "id": game_session.id,
            }
            serializer = GameSessionResponseSerializer(serializer_data)
            return JsonResponse(serializer.data, status=200)
        except GameBlockedException as e:
            return JsonResponse({"error": str(e)}, status=400)
        except Exception as e:
            logger.error(f"Error fetching session {str(e)}")

            return JsonResponse({"error": str(e)}, status=500)


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
            200: GameSessionUpdateResponseSerializer,
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
                session_words = {
                    "green_cards": data["green_cards"],
                    "red_cards": data["red_cards"],
                    "yellow_cards": data["yellow_cards"],
                }
                update_game_session(
                    game_session=game_session, session_words=session_words
                )

                # Update the game session stats
                game_stats = game_session.stats
                new_stats = GameSessionStatsSerializer(data=data["stats"])
                if new_stats.is_valid():
                    response.update(
                        update_game_session_stats(
                            new_stats=new_stats,
                            game_stats=game_stats,
                            green_cards=len(data["green_cards"]),
                            yellow_cards=len(data["yellow_cards"]),
                            red_cards=len(data["red_cards"]),
                        )
                    )
                # Update user stats
                response.update(
                    update_user_stats(user=request.user, game_stats=game_stats)
                )
                print(response)
                serializer = GameSessionUpdateResponseSerializer(response)
                return JsonResponse(serializer.data, status=200)

        except UserStatistics.DoesNotExist:
            today = timezone.now().date()
            UserStatistics.objects.create(
                user=request.user,
                last_day_played=today,
                days_streak=1,
                longest_streak=1,
            )
            return JsonResponse(
                GameSessionUpdateResponseSerializer(response), status=200
            )

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

            return Response(serializer.data, status=200)
        except Exception as e:
            return JsonResponse({"error": f"{e}"}, status=400)
