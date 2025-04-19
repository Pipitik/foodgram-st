import json
from django.core.management.base import BaseCommand
from tqdm import tqdm

from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Load ingredients from a JSON file"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Path to the JSON file")

    def handle(self, *args, **kwargs):
        file_path = kwargs["file_path"]
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            Ingredient.objects.all().delete()
            for item in tqdm(data, ncols=100, desc="Loading"):
                name = item.get("name")
                measurement_unit = item.get("measurement_unit")

                if name and measurement_unit:
                    Ingredient.objects.get_or_create(
                        name=name,
                        measurement_unit=measurement_unit
                    )
            self.stdout.write(self.style.SUCCESS("Ingredients loaded successfully!"))
        except Exception as error:
            self.stderr.write(self.style.ERROR(f"Error: {error}"))
   