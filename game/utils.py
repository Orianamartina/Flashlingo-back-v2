import json

from .models import GermanWord
from .serializers import GermanWordSerializer


def json_to_database(limit=None):
    """
    Fills the database using the data json file
    """
    with open("./updated_data.json", "r") as file:
        dictionary = json.load(file)
        data = dictionary["data"]
    # Connect to the MySQL database
    if limit:
        data = data[:limit]
    # Iterate over each entry in the JSON data
    for entry in data:

        # Create the German word object
        word_data = {
            "word": entry["german"],
            "article": entry["article"] or "null",
            "word_type": entry["type"] or "null",
        }
        word_serializer = GermanWordSerializer(data=word_data)

        if word_serializer.is_valid():
            german_word = word_serializer.save()  # Save and get the instance
        else:
            print(f"Word serializer errors: {word_serializer.errors}")
            continue  # Skip if the word is invalid

        # Create the sentences and associate them with the German word
        for sentence_text in entry["sentences"]:
            if sentence_text != "null":  # Skip if the sentence is null
                sentence_data = {
                    "german_word": german_word.id,
                    "sentence": sentence_text,
                }
                sentence_serializer = SentenceSerializer(data=sentence_data)
                if sentence_serializer.is_valid():
                    sentence_serializer.save()
                else:
                    print(f"Sentence serializer errors: {sentence_serializer.errors}")

        # Create the translations and associate them with the German word
        for translation_text in entry["translations"]:
            if translation_text != "null":  # Skip if the translation is null
                translation_data = {
                    "german_word": german_word.id,
                    "translation": translation_text,
                }
                translation_serializer = TranslationSerializer(data=translation_data)
                if translation_serializer.is_valid():
                    translation_serializer.save()
                else:
                    print(
                        f"Translation serializer errors: {translation_serializer.errors}"
                    )


def get_words_for_game_session(level: int):
    """
    Retrieves a list of German words for the given game level.

    :param level: The level of the game session.
    :return: A queryset of GermanWord objects corresponding to the level.
    """
    start_index = (level - 1) * 50
    end_index = level * 50
    return GermanWord.objects.all()[start_index:end_index]


def setup_game_sessions(user: User):
    new_stats = GameSessionStats.objects.create(level=1, user_id=user.id)
    new_stats.unlock()
    new_stats.save()
    GameSession.objects.create(level=1, user_id=user.id, stats=new_stats)

    for i in range(1, 20):
        new_stats = GameSessionStats.objects.create(level=i + 1, user_id=user.id)
        GameSession.objects.create(level=i + 1, user_id=user.id, stats=new_stats)
