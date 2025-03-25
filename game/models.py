from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.utils import timezone


class GermanWord(models.Model):
    word = models.CharField(max_length=200, unique=True)
    article = models.CharField(max_length=200)
    word_type = models.CharField(max_length=200)

    def __str__(self):
        return self.word


class Sentence(models.Model):
    german_word = models.ForeignKey(
        GermanWord, on_delete=models.CASCADE, related_name="sentences"
    )
    sentence = models.CharField(max_length=200)


class Translation(models.Model):
    german_word = models.ForeignKey(
        GermanWord, on_delete=models.CASCADE, related_name="translations"
    )
    translation = models.CharField(max_length=200)


class UserStatistics(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    days_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_day_played = models.DateField(default=timezone.now)
    highest_level = models.IntegerField(default=1)

    def __str__(self):
        return self.user.username


class GameSessionStats(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    level = models.IntegerField("Level", default=1)
    blocked = models.BooleanField("Is blocked", default=True)
    green_cards = models.IntegerField("Number of green cards", default=0)
    yellow_cards = models.IntegerField("Number of yellow cards", default=0)
    red_cards = models.IntegerField("Number of red cards", default=0)
    total_time_played = models.IntegerField("Total time played", default=0)
    lowest_game_time = models.IntegerField("Lowest game time", default=0)
    total_responses = models.IntegerField("Total responses", default=0)
    highest_score = models.IntegerField("Highest score", default=0)
    highest_answer_streak = models.IntegerField("Highest answer streak", default=0)
    points = models.IntegerField("Points", default=0, editable=False)
    score = models.IntegerField("Score", default=0)

    def unlock(self):
        self.blocked = False

    def save(self, *args, **kwargs):
        self.points = (
            (self.green_cards * 2) + (self.yellow_cards * 1) + (self.red_cards * 0)
        )

        if (self.green_cards + self.yellow_cards + self.red_cards) > 50:
            raise ValueError("Total number of cards cannot exceed 50")

        super(GameSessionStats, self).save(*args, **kwargs)


class GameSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    isEmpty = models.BooleanField("Is empty", default=True)
    level = models.IntegerField(default=1)
    green_cards = models.ManyToManyField(
        "GermanWord", related_name="game_sessions_green"
    )
    yellow_cards = models.ManyToManyField(
        "GermanWord", related_name="game_sessions_yellow"
    )
    red_cards = models.ManyToManyField("GermanWord", related_name="game_sessions_red")
    unclassified_cards = models.ManyToManyField(
        "GermanWord", related_name="game_sessions_unc"
    )
    stats = models.ForeignKey(
        GameSessionStats,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"{self.user.username}, level: {self.level}"
