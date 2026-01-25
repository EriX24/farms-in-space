from scripts.assets import FarmAssets
from scripts.environment_effects import EffectsLoadingManager, effects, Grass
from scripts.logger import log_error


def register(pygame_module, clock_, **surfaces):
    global pygame
    global clock
    global screens

    pygame = pygame_module
    clock = clock_
    screens = surfaces


effect_loading_manager = EffectsLoadingManager()


class Farm:
    def __init__(self, x: int):
        # X location
        self.x = x

        # All plants currently in the farm
        self.plants = []

        # The default environment
        self.environment = "default"

        # Gases provided by the plants
        self.provided_items = {}

        # Gases provided by the dispenser [???]
        self.environment_items = {}

        # Add grass to the list of effects
        grass = Grass()
        self.effects = [grass]
        self.effects_added = False

        # Apply the default effects
        self.add_effects()

    def blit(self):
        # Blit the farm box
        screens["centered_display"].blit(FarmAssets.farm_box, (self.x, 248))

        # Add the effects if they haven't been added yet
        if not self.effects_added:
            self.effects = []
            self.effects_added = True

        # Blit each effect
        for effect in self.effects:
            effect.blit(self)

    def update(self, player, pressed_keys, pickup_ready, dispenser):
        # Update each plant
        for plant in self.plants:
            plant.update(player, pressed_keys, pickup_ready, self, dispenser)

        # Apply effects if they haven't been applied yet
        if not self.effects_added:
            self.add_effects()

        # Update each effect
        for effect in self.effects:
            effect.update(player, pressed_keys, pickup_ready, self)

    def add_effects(self):
        """Apply the effects for the current environment"""
        new_effects = []
        self.effects_added = True

        for effect in effect_loading_manager.references.get(self.environment, []):
            if effects.get(effect):
                # Append the effect for the current environment
                new_effects.append(effects[effect]())
            else:
                # Error
                log_error("Environment effect failed to load, "
                          "most likely a typo in the effects register .json or a unregistered effect", self)

        # Add every new effect
        for effect in new_effects:
            self.effects.append(effect)

    def add_plant(self, plant):
        self.plants.append(plant)
