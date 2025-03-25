# Generated by Django 5.0.7 on 2024-12-15 23:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0005_gamesessionstats_blocked_gamesessionstats_points'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='germanword',
            name='sentence_1',
        ),
        migrations.RemoveField(
            model_name='germanword',
            name='sentence_2',
        ),
        migrations.RemoveField(
            model_name='germanword',
            name='sentence_3',
        ),
        migrations.RemoveField(
            model_name='germanword',
            name='translation_1',
        ),
        migrations.RemoveField(
            model_name='germanword',
            name='translation_2',
        ),
        migrations.RemoveField(
            model_name='germanword',
            name='translation_3',
        ),
        migrations.AddField(
            model_name='userstatistics',
            name='highest_level',
            field=models.IntegerField(default=1),
        ),
        migrations.CreateModel(
            name='Sentence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sentence', models.CharField(max_length=200)),
                ('german_word', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sentences', to='game.germanword')),
            ],
        ),
        migrations.CreateModel(
            name='Translation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('translation', models.CharField(max_length=200)),
                ('german_word', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='game.germanword')),
            ],
        ),
    ]
