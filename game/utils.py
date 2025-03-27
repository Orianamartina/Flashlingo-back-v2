import json
import hashlib
from datetime import timedelta

from django.utils import timezone
from django.contrib.auth.models import User

from game.serializers import GameSessionStatsSerializer
from .models import GameSession, GameSessionStats, UserStatistics, word_collection


def generate_id(word: str) -> str:
    """Generates a consistent ID for each word using a hash function."""
    return hashlib.sha256(word.encode()).hexdigest()[:24]


def json_to_database(limit=None):
    """
    Fills the database using the data JSON file.
    Ensures words get the same ID each time it runs.
    """
    with open("./dictionary/dictionary.json", "r") as file:
        dictionary = json.load(file)
        data = dictionary.get("data", [])

    if limit:
        data = data[:limit]
    print(data)
    for entry in data:
        print(entry)
        word = entry.get("german", "").strip()
        if not word:
            print("Skipping entry with missing word.")
            continue

        word_id = generate_id(word)

        existing_word = word_collection.find_one({"_id": word_id})
        if existing_word:
            print(f"Word '{word}' already exists, updating data.")

        word_data = {"_id": word_id, "word": word, "types": []}

        for word_type in entry.get("types", []):
            type_name = word_type.get("name", "unknown")
            translations = word_type.get("translations", [])
            article = word_type.get("article", None)
            examples = []

            for example in word_type.get("examples", []):
                sentence = example.get("sentence", "").strip()
                translation = example.get("translation", "").strip()
                if sentence and translation:
                    examples.append({"sentence": sentence, "translation": translation})

            word_data["types"].append(
                {
                    "name": type_name,
                    "translations": translations,
                    "examples": examples,
                    "article": article,
                }
            )

        word_collection.update_one({"_id": word_id}, {"$set": word_data}, upsert=True)

    print("Database update completed.")


def get_words_for_game_session(level: int):
    """
    Retrieves a list of German words for the given game level from MongoDB.

    :param level: The level of the game session.
    :return: A list of GermanWord dictionaries corresponding to the level.
    """

    start_index = (level - 1) * 50

    words = list(word_collection.find().skip(start_index).limit(50))
    return words


def setup_game_sessions(user: User):
    """
    Sets up initial game sessions for the user.
    """
    new_stats = GameSessionStats.objects.create(level=1, user_id=user.id)
    new_stats.unlock()
    new_stats.save()
    GameSession.objects.create(level=1, user_id=user.id, stats=new_stats)

    for i in range(1, 20):
        new_stats = GameSessionStats.objects.create(level=i + 1, user_id=user.id)
        GameSession.objects.create(level=i + 1, user_id=user.id, stats=new_stats)


def update_user_stats(user: User, game_stats: any):
    """
    Function to update user stats after finishing a game session
    """
    achievements = {}
    user_stats = UserStatistics.objects.get(user=user)
    if game_stats.level == user_stats.highest_level and game_stats.points >= 70:
        user_stats.highest_level += 1
        user_stats.save()
        next_level = GameSessionStats.objects.get(level=game_stats.level + 1, user=user)
        next_level.unlock()
        next_level.save()
        achievements["new_level"] = True

    today = timezone.now().date()
    stats = UserStatistics.objects.get(user=user)

    if stats.last_day_played == today - timedelta(days=1):
        stats.days_streak += 1
    if stats.days_streak > stats.longest_streak:
        stats.longest_streak = stats.days_streak
    else:
        stats.days_streak = 1

    stats.last_day_played = today
    stats.save()

    return achievements


def update_game_session_stats(
    new_stats: GameSessionStatsSerializer,
    game_stats: GameSessionStats,
    green_cards: int,
    yellow_cards: int,
    red_cards: int,
):
    """
    Function to update the game session stats after finishing
    """
    achievements = {}
    new_stats_data = new_stats.validated_data

    game_stats.green_cards = green_cards
    if game_stats.green_cards == 50:
        achievements["full_green"] = True
    game_stats.yellow_cards = yellow_cards
    game_stats.red_cards = red_cards
    game_stats.total_time_played += new_stats_data["total_time_played"]
    game_stats.score += new_stats_data["score"]
    if (
        game_stats.lowest_game_time == 0
        or game_stats.lowest_game_time > new_stats_data["total_time_played"]
    ):
        game_stats.lowest_game_time = new_stats_data["total_time_played"]
        achievements["lowest_game_time"] = True

    game_stats.total_responses += new_stats_data["total_responses"]
    if game_stats.highest_score < new_stats_data["score"]:
        achievements["highest_score"] = True
    game_stats.highest_score = max(game_stats.highest_score, new_stats_data["score"])
    game_stats.highest_answer_streak = max(
        game_stats.highest_answer_streak,
        new_stats_data["highest_answer_streak"],
    )
    game_stats.save()

    return achievements


def update_game_session(game_session: GameSession, session_words: dict[str, any]):
    """
    Function to update game session
    """
    # Check if the number of cards is valid
    if (
        len(session_words["green_cards"])
        + len(session_words["yellow_cards"])
        + len(session_words["red_cards"])
    ) < 50:
        raise Exception("Invalid number of cards")

    # Clear the existing cards
    game_session.red_cards.clear()
    game_session.yellow_cards.clear()
    game_session.green_cards.clear()
    game_session.unclassified_cards.clear()

    empty_cards = 0

    for classification, words in session_words.items():
        if len(words) == 0:
            empty_cards += 1
        for word in words:
            german_word = word_collection.find_one({"_id": word})

            if not german_word:
                raise Exception(f"Word with id {word} not found in MongoDB")

            if classification == "green_cards":
                game_session.green_cards.append(str(german_word["_id"]))
            elif classification == "yellow_cards":
                game_session.yellow_cards.append(str(german_word["_id"]))
            elif classification == "red_cards":
                game_session.red_cards.append(str(german_word["_id"]))

    if empty_cards == 4:
        raise Exception("Too many empty card classifications")

    game_session.save()
