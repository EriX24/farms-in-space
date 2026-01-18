# TODO: Make each farm into its own object
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
        self.x = x
        self.plants = []
        self.environment = "default"
        self.provided_items = {}
        self.environment_items = {}
        grass = Grass()
        self.effects = [grass]
        self.effects_added = False

        self.add_effects()

    def blit(self):
        screens["centered_display"].blit(FarmAssets.farm_box, (self.x, 248))

        if not self.effects_added:
            self.effects = []
            self.effects_added = True

        for effect in self.effects:
            effect.blit(self)

    def update(self, player, pressed_keys, pickup_ready, dispenser):
        for plant in self.plants:
            plant.update(player, pressed_keys, pickup_ready, self, dispenser)  # TODO: Follow the trail

        if not self.effects_added:
            self.add_effects()

        for effect in self.effects:
            effect.update(player, pressed_keys, pickup_ready, self)

    def add_effects(self):
        new_effects = []
        self.effects_added = True

        for effect in effect_loading_manager.references.get(self.environment, []):
            if effects.get(effect):
                new_effects.append(effects[effect]())
            else:

                log_error("Environment effect failed to load, "
                          "most likely a typo in the effects register .json or a unregistered effect", self)

        for effect in new_effects:
            self.effects.append(effect)

    def add_plant(self, plant):
        self.plants.append(plant)
