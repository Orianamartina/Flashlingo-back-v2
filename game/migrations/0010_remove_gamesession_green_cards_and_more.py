# Generated by Django 5.0.7 on 2025-02-03 00:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0009_gamesessionstats_score'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gamesession',
            name='green_cards',
        ),
        migrations.RemoveField(
            model_name='gamesession',
            name='yellow_cards',
        ),
        migrations.RemoveField(
            model_name='gamesession',
            name='red_cards',
        ),
        migrations.RemoveField(
            model_name='translation',
            name='german_word',
        ),
        migrations.RemoveField(
            model_name='gamesession',
            name='unclassified_cards',
        ),
        migrations.AddField(
            model_name='gamesession',
            name='green_cards',
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name='gamesession',
            name='yellow_cards',
            field=models.JSONField(default=list),
        ),
        migrations.DeleteModel(
            name='Sentence',
        ),
        migrations.AddField(
            model_name='gamesession',
            name='red_cards',
            field=models.JSONField(default=list),
        ),
        migrations.DeleteModel(
            name='Translation',
        ),
        migrations.DeleteModel(
            name='GermanWord',
        ),
        migrations.AddField(
            model_name='gamesession',
            name='unclassified_cards',
            field=models.JSONField(default=list),
        ),
    ]
