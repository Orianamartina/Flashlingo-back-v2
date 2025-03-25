from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from game.utils import json_to_database


def get_url_for_game_session(user, level):
    return reverse("get_or_create_game_session", args=[user, level])


def get_url_for_game_session_update(session_id):
    return reverse("update_game_session", args=[session_id])


class SetupUserGamesTests(TestCase):
    """
    Test cases for setting up games
    """

    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse("login")
        self.user = User.objects.create_user(
            username="testuser", password="testpassword", email="testuser@example.com"
        )

        json_to_database(limit=100)

    def test_user_can_create_new_game_session_and_update_it(self):
        game_session_url = get_url_for_game_session(1, 1)
        save_game_session_url = get_url_for_game_session_update(1)
        login_response = self.client.post(
            self.login_url,
            {"username": "testuser", "password": "testpassword"},
            format="json",
        )
        data = login_response.json()
        response = self.client.get(
            game_session_url,
            HTTP_AUTHORIZATION=f"Bearer {data['access']}",
            format="json",
        )
        response_data = response.json()
        unclassified_cards = response_data["unclassified_cards"]
        self.assertEqual(len(unclassified_cards), 100)

        updated_session_cards = {
            "green_cards": [],
            "yellow_cards": [],
            "red_cards": unclassified_cards,
            "unclassified_cards": [],
        }
        self.client.post(
            save_game_session_url,
            updated_session_cards,
            HTTP_AUTHORIZATION=f"Bearer {data['access']}",
            format="json",
        )

        updated_session = self.client.get(
            game_session_url,
            HTTP_AUTHORIZATION=f"Bearer {data['access']}",
            format="json",
        )
        updated_session_data = updated_session.json()
        self.assertEqual(len(updated_session_data["unclassified_cards"]), 0)
        self.assertEqual(len(updated_session_data["red_cards"]), 100)
        self.assertEqual(updated_session_data["red_cards"], unclassified_cards)

    def test_game_session_update_cant_be_empty(self):
        game_session_url = get_url_for_game_session(1, 1)
        save_game_session_url = get_url_for_game_session_update(1)
        login_response = self.client.post(
            self.login_url,
            {"username": "testuser", "password": "testpassword"},
            format="json",
        )
        data = login_response.json()
        self.client.get(
            game_session_url,
            HTTP_AUTHORIZATION=f"Bearer {data['access']}",
            format="json",
        )
        updated_session_cards = {
            "green_cards": [],
            "yellow_cards": [],
            "red_cards": [],
            "unclassified_cards": [],
        }
        update_response = self.client.post(
            save_game_session_url,
            updated_session_cards,
            HTTP_AUTHORIZATION=f"Bearer {data['access']}",
            format="json",
        )

        self.assertEqual(update_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_a_session_cant_save_another_levels_words(self):
        game_session_url = get_url_for_game_session(1, 1)
        game_session_url_2 = get_url_for_game_session(1, 2)
        save_game_session_url_2 = get_url_for_game_session_update(2)

        login_response = self.client.post(
            self.login_url,
            {"username": "testuser", "password": "testpassword"},
            format="json",
        )
        data = login_response.json()
        self.client.get(
            game_session_url,
            HTTP_AUTHORIZATION=f"Bearer {data['access']}",
            format="json",
        )
        level_2 = self.client.get(
            game_session_url_2,
            HTTP_AUTHORIZATION=f"Bearer {data['access']}",
            format="json",
        ).json()

        updated_session_cards = {
            "green_cards": level_2["green_cards"],
            "yellow_cards": level_2["yellow_cards"],
            "red_cards": level_2["red_cards"],
            "unclassified_cards": level_2["unclassified_cards"],
        }
        update_response = self.client.post(
            save_game_session_url_2,
            updated_session_cards,
            HTTP_AUTHORIZATION=f"Bearer {data['access']}",
            format="json",
        )
        print(update_response.json())
        self.assertEqual(update_response.status_code, 400)
