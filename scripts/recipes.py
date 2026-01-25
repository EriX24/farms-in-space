import os
import json
import pygame
from scripts.logger import log_error


class RecipeManager:
    def __init__(self):
        # All recipies
        self.recipes = {}

        # Load the recipies
        self.load_recipes()

    def load_recipes(self):
        # Loop through every json file in assets/recipes/data
        for recipe in os.listdir(os.path.join("assets", "recipes", "data")):
            if recipe.endswith(".json"):
                try:
                    # Try getting the recipy data
                    recipe_data = json.load(open(os.path.join("assets", "recipes", "data", recipe)))

                    if recipe_data.get("id"):
                        # Register the recipy
                        self.recipes[recipe_data["id"]] = recipe_data

                        # Register the blueprint
                        self.recipes[recipe_data["id"]]["blueprint"] = pygame.image.load(
                            os.path.join("assets", "recipes", "blueprints",
                                         self.recipes[recipe_data["id"]]["blueprint"]) + ".png")

                    else:
                        # No recipy ID
                        log_error("No ID", self)

                except json.decoder.JSONDecodeError:
                    # Json file has errors
                    log_error("Corrupted JSON file", self)


class EnvironmentRecipeManager:
    def __init__(self):
        # All recipies
        self.recipes = {}

        # Load the recipies
        self.load_recipes()

    def load_recipes(self):
        # Loop through every json file in assets/environ/data
        for recipe in os.listdir(os.path.join("assets", "environ", "data")):
            if recipe.endswith(".json"):
                try:
                    # Try getting the recipy data
                    recipe_data = json.load(open(os.path.join("assets", "environ", "data", recipe)))

                    if recipe_data.get("id"):
                        # Register the recipy
                        self.recipes[recipe_data["id"]] = recipe_data

                        # Register the blueprint
                        self.recipes[recipe_data["id"]]["blueprint"] = pygame.image.load(
                            os.path.join("assets", "environ", "blueprints",
                                         self.recipes[recipe_data["id"]]["blueprint"]) + ".png")

                    else:
                        # No recipy ID
                        log_error("No ID", self)

                except json.decoder.JSONDecodeError:
                    # Json file has errors
                    log_error("Corrupted JSON file", self)
