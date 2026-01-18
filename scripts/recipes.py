import os
import json
import pygame
from scripts.logger import log_error


class RecipeManager:
    def __init__(self):
        self.recipes = {}

        self.load_recipes()

    def load_recipes(self):
        for recipe in os.listdir(os.path.join("assets", "recipes", "data")):
            if recipe.endswith(".json"):
                try:
                    recipe_data = json.load(open(os.path.join("assets", "recipes", "data", recipe)))

                    if recipe_data.get("id"):
                        self.recipes[recipe_data["id"]] = recipe_data
                        self.recipes[recipe_data["id"]]["blueprint"] = pygame.image.load(
                            os.path.join("assets", "recipes", "blueprints",
                                         self.recipes[recipe_data["id"]]["blueprint"]) + ".png")

                    else:
                        log_error("No ID", self)

                except json.decoder.JSONDecodeError:
                    log_error("Corrupted JSON file", self)


class EnvironmentRecipeManager:
    def __init__(self):
        self.recipes = {}
        self.load_recipes()

    def load_recipes(self):
        for recipe in os.listdir(os.path.join("assets", "environ", "data")):
            if recipe.endswith(".json"):
                try:
                    recipe_data = json.load(open(os.path.join("assets", "environ", "data", recipe)))

                    if recipe_data.get("id"):
                        self.recipes[recipe_data["id"]] = recipe_data
                        self.recipes[recipe_data["id"]]["blueprint"] = pygame.image.load(
                            os.path.join("assets", "environ", "blueprints",
                                         self.recipes[recipe_data["id"]]["blueprint"]) + ".png")

                    else:
                        log_error("No ID", self)

                except json.decoder.JSONDecodeError:
                    log_error("Corrupted JSON file", self)
