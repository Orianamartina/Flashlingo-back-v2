from django.contrib.auth.models import User
from django.db import models

from flashlingo.db_connection import db

# Create your models here.
from django.utils import timezone


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
    green_cards = models.JSONField(default=list)
    yellow_cards = models.JSONField(default=list)
    red_cards = models.JSONField(default=list)
    unclassified_cards = models.JSONField(default=list)
    stats = models.ForeignKey(
        GameSessionStats,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"{self.user.username}, level: {self.level}"


word_collection = db["GermanWord"]
