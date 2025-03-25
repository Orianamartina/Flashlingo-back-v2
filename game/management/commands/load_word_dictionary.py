from django.core.management.base import BaseCommand
from game.utils import json_to_database
from game.models import GermanWord


class Command(BaseCommand):
    help = "Setup German dictionary"

    def handle(self, *args, **options) -> None:
        try:
            already_full = GermanWord.objects.exists()

            if already_full:
                self.stdout.write(
                    self.style.SUCCESS("German dictionary is already populated.")
                )
            else:
                json_to_database()
                self.stdout.write(
                    self.style.SUCCESS("German dictionary has been populated.")
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {str(e)}"))
