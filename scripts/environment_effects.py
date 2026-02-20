import os
import json
import random

from scripts.assets import FarmAssets
from scripts.logger import log_error

effects = {}


def register(pygame_module, clock_, **surfaces):
    global pygame
    global clock
    global screens

    pygame = pygame_module
    clock = clock_
    screens = surfaces


def register_effect(name: str, effect):
    """Registers an effect"""
    effects[name] = effect


class EffectsLoadingManager:
    def __init__(self):
        self.references = {}
        self.load_recipes()

    def load_recipes(self):
        for reference in os.listdir(os.path.join("assets", "environ", "effects")):
            if reference.endswith(".json"):
                try:
                    reference_data = json.load(open(os.path.join("assets", "environ", "effects", reference)))

                    if reference_data.get("effects") and type(reference_data.get("effects")) is list:

                        self.references[reference_data.get("environment")] = reference_data.get("effects")

                    else:
                        log_error("No Effects or Effects is not in required format", self)

                except json.decoder.JSONDecodeError:
                    log_error("Corrupted JSON file", self)


# Default dirt
class Dirt:
    def __init__(self):
        self.opacity = 0

        # How long before the dirt is removed
        self.destruct_cd = 0

        # Copy the image to avoid referencing the same data in memory and messing this up
        self.image = FarmAssets.dirt.copy()

    def blit(self, farm):
        self.image.set_alpha(self.opacity)

        # The dirt will always be there
        if farm.environment:
            screens["centered_display"].blit(self.image, (farm.x, 248))

    def update(self, player, pressed_keys, pickup_ready, farm):
        effect_count = 0  # How many dirt already exist
        for effect in farm.effects:
            if effect.__class__ == self.__class__:
                effect_count += 1

        if effect_count >= 2 and self.destruct_cd <= 0:
            farm.effects.remove(self)

        if farm.environment == "default:default":
            self.destruct_cd = 255
        else:
            if self.destruct_cd <= 0:
                farm.effects.remove(self)

            self.destruct_cd -= 3

        self.opacity += 3


register_effect("default:dirt", Dirt)


# Default environment grass
class Grass:
    def __init__(self):
        # Opacity
        self.layer_1_opacity = 0
        self.layer_1b_opacity = 0
        self.layer_2_opacity = 0
        self.layer_3_opacity = 0

        # Opacity stuff
        self.OPACITY_INCREASE = 0.3
        self.OPACITY_DECREASE = 1.5

        # Layers
        self.layer_1 = []
        self.layer_1b = []
        self.layer_2 = []
        self.layer_3 = []

        # Layer images
        self.layer_1_image = FarmAssets.grass_canvas.copy()
        self.layer_2_image = FarmAssets.grass_canvas.copy()
        self.layer_3_image = FarmAssets.grass_canvas.copy()
        self.layer_1b_image = FarmAssets.grass_canvas.copy()
        self.image = FarmAssets.grass_canvas.copy()

        # Update timer
        self.update_cooldown = 50
        self.update_timer = 0

        # Reference for a filled layer
        self.filled_layer = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23,
                             24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44,
                             45, 46]

    def blit(self, farm):

        if farm.effects.index(self) == len(farm.effects) - 1:
            # Layer 1
            layer_1_copy = self.layer_1_image.copy()
            layer_1_copy.set_alpha(self.layer_1_opacity)
            self.image.blit(layer_1_copy, (0, 0))
            del layer_1_copy

            # Layer 1b ("buffer" layer)
            layer_1b_copy = self.layer_1b_image.copy()
            layer_1b_copy.set_alpha(self.layer_1b_opacity)
            self.image.blit(layer_1b_copy, (0, 0))
            del layer_1b_copy

            # Layer 2
            layer_2_copy = self.layer_2_image.copy()
            layer_2_copy.set_alpha(self.layer_2_opacity)
            self.image.blit(layer_2_copy, (0, 0))
            del layer_2_copy

            # UNUSED
            # layer_2b_copy = self.layer_2b_image.copy()
            # layer_2b_copy.set_alpha(self.layer_2b_opacity)
            # self.image.blit(layer_2b_copy, (0, 0))
            # del layer_2b_copy

            # Layer 3
            layer_3_copy = self.layer_3_image.copy()
            layer_3_copy.set_alpha(self.layer_3_opacity)
            self.image.blit(layer_3_copy, (0, 0))
            del layer_3_copy

            # UNUSED
            # layer_3b_copy = self.layer_3b_image.copy()
            # layer_3b_copy.set_alpha(self.layer_3b_opacity)
            # self.image.blit(layer_3b_copy, (0, 0))
            # del layer_3b_copy

            # Blit the effect
            screens["centered_display"].blit(self.image, (farm.x, 248))

            # Reset the image to prevent the transparent images from stacking
            self.image = FarmAssets.grass_canvas.copy()

        else:
            # Force grass to be at the front
            farm.effects.remove(self)
            farm.effects.append(self)

        # Used for testing list overflow
        # print(self.layer_1, "\n", self.layer_2, "\n", self.layer_2b, "\n", self.layer_3, "\n", self.layer_3b)

    def update(self, player, pressed_keys, pickup_ready, farm):
        # Update timer
        self.update_timer += clock.get_time()

        # Effect update
        for _ in range(self.update_timer // self.update_cooldown):
            if farm.environment == "default:default":
                self.grow_layer()

            """ Old Code
            if not self.layer_1:
                # Layer 1 and layer 1b creation
                self.layer_1 = self.filled_layer.copy()
                self.layer_1b = self.filled_layer.copy()

                for pixel in self.layer_1:
                    self.layer_1[pixel] = [pixel, 0]
                    self.layer_1b[pixel] = [pixel, 0]

                for _ in range(2):
                    # Random detail
                    random_pixel = random.choice(self.layer_1)
                    pixel_idx = self.layer_1.index(random_pixel)

                    self.layer_1[pixel_idx] = [random_pixel[0], random.randint(2, 3)]

                for _ in range(2):
                    # Random detail (1b)
                    random_pixel = random.choice(self.layer_1b)
                    pixel_idx = self.layer_1b.index(random_pixel)

                    self.layer_1b[pixel_idx] = [random_pixel[0], random.randint(2, 3)]


            elif self.layer_1_opacity >= 255 and self.layer_1b_opacity >= 255 and not self.layer_2:
                # Layer 2 creation
                for _ in range(15):
                    loc_choice = random.choice(self.filled_layer)
                    loc_area = [loc_choice - 3, loc_choice - 2, loc_choice - 1, loc_choice, loc_choice + 1,
                                loc_choice + 2, loc_choice + 3]

                    for pixel in loc_area:
                        # If the pixel exists in layer 1 and doesn't already exist in layer 2 (to prevent pixel overlap)
                        if pixel in [pixel_[0] for pixel_ in self.layer_1] and pixel not in [pixel_[0] for pixel_ in
                                                                                             self.layer_2]:
                            self.layer_2.append([pixel, 0])

                for _ in range(2):
                    # Random detail
                    random_pixel = random.choice(self.layer_2)
                    pixel_idx = self.layer_2.index(random_pixel)

                    self.layer_2[pixel_idx] = [random_pixel[0], random.randint(2, 3)]

            elif self.layer_2_opacity >= 255 and not self.layer_3:
                # Layer 3 creation
                for _ in range(10):
                    loc_choice = random.choice(self.layer_2)
                    loc_area = [loc_choice[0] - 3, loc_choice[0] - 2, loc_choice[0] - 1, loc_choice[0],
                                loc_choice[0] + 1, loc_choice[0] + 2, loc_choice[0] + 3]

                    for pixel in loc_area:
                        # Special conditions are used to make the grass more convincing (not forming a precipice)
                        condition_1 = pixel in [p[0] for p in self.layer_2]
                        condition_2 = pixel - 1 in [p[0] for p in self.layer_2] or pixel - 1 < 0
                        condition_3 = pixel + 1 in [p[0] for p in self.layer_2] or pixel + 1 > 46

                        if condition_1 and condition_2 and condition_3 and pixel not in [pixel_[0] for pixel_ in
                                                                                         self.layer_3]:
                            # If the doesn't already exist in layer 3 (to prevent pixel overlap)
                            self.layer_3.append([pixel, 0])

                for _ in range(1):
                    # Random detail
                    random_pixel = random.choice(self.layer_3)
                    pixel_idx = self.layer_3.index(random_pixel)

                    self.layer_3[pixel_idx] = [random_pixel[0], random.randint(2, 3)]
            """

            # # UNUSED
            # elif self.layer_3 and not self.layer_3b:
            #     for _ in range(2):
            #         loc_choice = random.choice(self.filled_layer)
            #         loc_area = [loc_choice - 3, loc_choice - 2, loc_choice - 1, loc_choice, loc_choice + 1,
            #                     loc_choice + 2, loc_choice + 3]
            #
            #         for pixel in loc_area:
            #             condition_1 = pixel in [pixel[0] for pixel in self.layer_2]
            #             condition_2 = pixel - 1 in [pixel[0] for pixel in self.layer_2] or pixel - 1 < 0
            #             condition_3 = pixel + 1 in [pixel[0] for pixel in self.layer_2] or pixel + 1 > 46
            #             if condition_1 and condition_2 and condition_3:
            #                 self.layer_3b.append(pixel)

            # Opacity increase every update
            if (farm.environment == "default:default" and self.layer_3_opacity < 255) or (
                    farm.environment != "default:default" and self.layer_1 != []):
                for _ in range(clock.get_time()):
                    if self.layer_1_opacity < 255 and farm.environment == "default:default":
                        self.layer_1_opacity += self.OPACITY_INCREASE
                        self.layer_1_opacity = round(self.layer_1_opacity, 1) / 0.3 * 0.3
                    elif not self.layer_1b and farm.environment != "default:default":
                        self.layer_1_opacity -= self.OPACITY_DECREASE
                        if self.layer_1_opacity < 0:
                            self.layer_1 = []
                            self.layer_1_opacity = 0
                            break

                    if self.layer_1b and self.layer_1b_opacity < 255 <= self.layer_1_opacity and farm.environment == "default:default":
                        self.layer_1b_opacity += self.OPACITY_INCREASE
                        self.layer_1b_opacity = round(self.layer_1b_opacity, 1) / 0.3 * 0.3
                    elif not self.layer_2 and farm.environment != "default:default":
                        self.layer_1b_opacity -= self.OPACITY_DECREASE
                        if self.layer_1b_opacity < 0:
                            self.layer_1b = []
                            self.layer_1b_image = FarmAssets.grass_canvas.copy()
                            self.layer_1b_opacity = 0

                    if self.layer_2 and self.layer_2_opacity < 255 and farm.environment == "default:default":
                        self.layer_2_opacity += self.OPACITY_INCREASE
                        self.layer_2_opacity = round(self.layer_2_opacity, 1) / 0.3 * 0.3
                    elif self.layer_3 == [] and farm.environment != "default:default":
                        self.layer_2_opacity -= self.OPACITY_DECREASE
                        if self.layer_2_opacity < 0:
                            self.layer_2 = []
                            self.layer_2_image = FarmAssets.grass_canvas.copy()
                            self.layer_2_opacity = 0

                    if self.layer_3 and self.layer_3_opacity < 255 and farm.environment == "default:default":
                        self.layer_3_opacity += self.OPACITY_INCREASE
                        self.layer_3_opacity = round(self.layer_3_opacity, 1) / 0.3 * 0.3
                    elif farm.environment != "default:default":
                        self.layer_3_opacity -= self.OPACITY_DECREASE
                        if self.layer_3_opacity < 0:
                            self.layer_3 = []
                            self.layer_3_image = FarmAssets.grass_canvas.copy()
                            self.layer_3_opacity = 0

            # # UNUSED
            # if self.layer_3 and self.layer_2b_opacity < 150:
            #     self.layer_2b_opacity += 1
            #
            # # UNUSED
            # if self.layer_3b and self.layer_3b_opacity < 100:
            #     self.layer_3b_opacity += 1

        # Show layer 1 pixels
        if self.layer_1:
            for pixel in self.layer_1:
                pixel_list = ["#117c13",
                              "#138510",
                              "#268b07",
                              "#41980a"]

                pygame.draw.rect(self.layer_1_image, pixel_list[pixel[1]], (4 + pixel[0] * 4, 220, 4, 4))

        # Show layer 1b pixels
        if self.layer_1b:
            for pixel in self.layer_1b:
                pixel_list = ["#117c13",
                              "#138510",
                              "#268b07",
                              "#41980a"]

                pygame.draw.rect(self.layer_1b_image, pixel_list[pixel[1]], (4 + pixel[0] * 4, 224, 4, 4))

        # Show layer 2 pixels
        if self.layer_2:
            for pixel in self.layer_2:
                pixel_list = ["#117c13",
                              "#138510",
                              "#268b07",
                              "#41980a"]

                # print(self.layer_2)
                pygame.draw.rect(self.layer_2_image, pixel_list[pixel[1]], (4 + pixel[0] * 4, 228, 4, 4))

        # # UNUSED
        # if self.layer_2b:
        #     for pixel in self.layer_2b:
        #         self.layer_2b_image.blit(FarmAssets.grass_pixel_0, (4 + pixel * 4, 224))

        # Show layer 3 pixels
        if self.layer_3:
            for pixel in self.layer_3:
                pixel_list = ["#117c13",
                              "#138510",
                              "#268b07",
                              "#41980a"]

                pygame.draw.rect(self.layer_3_image, pixel_list[pixel[1]], (4 + pixel[0] * 4, 232, 4, 4))

        # # UNUSED
        # if self.layer_3b:
        #     for pixel in self.layer_3b:
        #         self.layer_3b_image.blit(FarmAssets.grass_pixel_0, (4 + pixel * 4, 228))

        # Reset the cooldown
        self.update_timer %= self.update_cooldown

    def grow_layer(self):
        if not self.layer_1:
            # Layer 1 and layer 1b creation
            self.layer_1 = self.filled_layer.copy()
            self.layer_1b = self.filled_layer.copy()

            for pixel in self.layer_1:
                self.layer_1[pixel] = [pixel, 0]
                self.layer_1b[pixel] = [pixel, 0]

            for _ in range(2):
                # Random detail
                random_pixel = random.choice(self.layer_1)
                pixel_idx = self.layer_1.index(random_pixel)

                self.layer_1[pixel_idx] = [random_pixel[0], random.randint(2, 3)]

            for _ in range(2):
                # Random detail (1b)
                random_pixel = random.choice(self.layer_1b)
                pixel_idx = self.layer_1b.index(random_pixel)

                self.layer_1b[pixel_idx] = [random_pixel[0], random.randint(2, 3)]

        elif not self.layer_1b and self.layer_1:
            self.layer_1b = self.filled_layer.copy()

            for pixel in self.layer_1b:
                self.layer_1b[pixel] = [pixel, 0]

            for _ in range(2):
                # Random detail (1b)
                random_pixel = random.choice(self.layer_1b)
                pixel_idx = self.layer_1b.index(random_pixel)

                self.layer_1b[pixel_idx] = [random_pixel[0], random.randint(2, 3)]

        if self.layer_1b_opacity >= 255 and not self.layer_2:
            # Layer 2 creation
            for _ in range(15):
                loc_choice = random.choice(self.filled_layer)
                loc_area = [loc_choice - 3, loc_choice - 2, loc_choice - 1, loc_choice, loc_choice + 1,
                            loc_choice + 2, loc_choice + 3]

                for pixel in loc_area:
                    # If the pixel exists in layer 1 and doesn't already exist in layer 2 (to prevent pixel overlap)
                    if pixel in [pixel_[0] for pixel_ in self.layer_1] and pixel not in [pixel_[0] for pixel_ in
                                                                                         self.layer_2]:
                        self.layer_2.append([pixel, 0])

            for _ in range(2):
                # Random detail
                random_pixel = random.choice(self.layer_2)
                pixel_idx = self.layer_2.index(random_pixel)

                self.layer_2[pixel_idx] = [random_pixel[0], random.randint(2, 3)]

        if self.layer_2_opacity >= 255 and not self.layer_3:
            # Layer 3 creation
            for _ in range(10):
                loc_choice = random.choice(self.layer_2)
                loc_area = [loc_choice[0] - 3, loc_choice[0] - 2, loc_choice[0] - 1, loc_choice[0],
                            loc_choice[0] + 1, loc_choice[0] + 2, loc_choice[0] + 3, loc_choice[0] + 3]

                for pixel in loc_area:
                    # Special conditions are used to make the grass more convincing (not forming a precipice)
                    condition_1 = pixel in [p[0] for p in self.layer_2]
                    condition_2 = pixel - 1 in [p[0] for p in self.layer_2] or pixel - 1 < 0
                    condition_3 = pixel + 1 in [p[0] for p in self.layer_2] or pixel + 1 > 46

                    if condition_1 and condition_2 and condition_3 and pixel not in [pixel_[0] for pixel_ in
                                                                                     self.layer_3]:
                        # If the doesn't already exist in layer 3 (to prevent pixel overlap)
                        self.layer_3.append([pixel, 0])

            for _ in range(1):
                # Random detail
                random_pixel = random.choice(self.layer_3)
                pixel_idx = self.layer_3.index(random_pixel)

                self.layer_3[pixel_idx] = [random_pixel[0], random.randint(2, 3)]


register_effect("default:grass", Grass)


# Pale Environment Dirt
class PaleEnvironmentDirt(Dirt):
    def __init__(self):
        super().__init__()
        self.opacity = 0
        self.image = FarmAssets.pale_dirt.copy()

    # Needs a slightly different update, but doesn't need a different blit, so it saves space, just not much
    def update(self, player, pressed_keys, pickup_ready, farm):
        # Prevent duplication
        effect_count = 0
        for effect in farm.effects:
            if effect.__class__ == self.__class__:
                effect_count += 1

        if effect_count >= 2 and self.destruct_cd <= 0:
            farm.effects.remove(self)

        # Destruction timer
        if farm.environment == "default:pale":
            self.destruct_cd = 255
        else:
            if self.destruct_cd <= 0:
                farm.effects.remove(self)

            self.destruct_cd -= 3

        # Opacity
        self.opacity += 3


register_effect("default:pale-dirt", PaleEnvironmentDirt)


# Pale Environment Mist
class PaleEnvironmentBackground:
    def __init__(self):
        self.opacity = 0

    def blit(self, farm):
        overlay = FarmAssets.pale_environment_overlay.copy()
        overlay.set_alpha((80 / 255) * self.opacity)

        screens["centered_display"].blit(overlay, (farm.x, 248))

    def update(self, player, pressed_keys, pickup_ready, farm):
        # Count the number of "default:pale-environment-mist" in the effects
        count = 0
        for effect in farm.effects:
            if type(effect) == type(self):
                count += 1

        # Prevent it from being spammed
        if count > 1 and self.opacity <= 0:
            farm.effects.remove(self)

        # Add opacity if the environment matches and remove opacity if it doesn't
        if farm.environment == "default:pale":
            if self.opacity < 255: self.opacity += 3
        else:
            if self.opacity > 0: self.opacity -= 18

        # Remove the effect if it's invisible and the environment isn't 'pale'
        if self.opacity <= 0 and farm.environment != "default:pale":
            farm.effects.remove(self)


register_effect("default:pale-environment-mist", PaleEnvironmentBackground)


# Pale clouds
class PaleClouds:
    def __init__(self):
        # Clouds currently on screen
        self.clouds = []  # [[0, 40, 0]]

        # Cloud creation
        self.timer = 0
        self.CLOUD_CREATION_COOLDOWN = 2000  # 5 seconds

        # Cloud move timer
        self.cloud_move_timer = 0
        self.CLOUD_MOVE_COOLDOWN = 500  # 0.5 seconds

        # Canvas
        self.cloud_canvas = FarmAssets.blank_canvas.copy()

        # Rect
        self.rect = self.cloud_canvas.get_rect()

    def blit(self, farm):
        # 224, 248
        self.rect.left = farm.x + 4
        self.rect.bottom = 464

        # Display the clouds
        for cloud in self.clouds:
            cloud_img = FarmAssets.pale_cloud.copy()
            cloud_img.set_alpha(cloud[2])
            self.cloud_canvas.blit(cloud_img, (cloud[0], cloud[1]))
            del cloud_img

        # Blit
        screens["centered_display"].blit(self.cloud_canvas, self.rect)
        self.cloud_canvas = FarmAssets.blank_canvas.copy()

    def update(self, player, pressed_keys, pickup_ready, farm):
        self.timer += clock.get_time()
        self.cloud_move_timer += clock.get_time()

        if farm.environment != "default:pale":
            for _ in range(49):
                self.cloud_move_timer += clock.get_time()

        # Count the number of "default:pale-clouds" in the effects
        count = 0
        for effect in farm.effects:
            if type(effect) == type(self):
                count += 1

        # Remove the effect if...
        if not self.clouds and farm.environment != "default:pale":
            # There are no clouds and the environment isn't pale
            farm.effects.remove(self)
        elif self.clouds == [] and count > 1:
            # There aare other cloud effects loaded and this one doesn't have any clouds
            farm.effects.remove(self)

        # Cloud creation
        if self.timer // self.CLOUD_CREATION_COOLDOWN and farm.environment == "default:pale":
            for _ in range(self.timer // self.CLOUD_CREATION_COOLDOWN):
                self.clouds.append([random.randint(-40, 240) // 4 * 4, random.randint(40, 200) // 4 * 4, 0])

        # Moving the clouds
        if self.cloud_move_timer > self.CLOUD_MOVE_COOLDOWN:
            for _ in range(self.cloud_move_timer // self.CLOUD_MOVE_COOLDOWN):
                for cloud_idx in range(len(self.clouds)):
                    self.clouds[cloud_idx][1] -= 4
                    if self.clouds[cloud_idx][2] < 20:
                        self.clouds[cloud_idx][2] += 5

        # Destroy and offscreen clouds
        for cloud_idx in range(len(self.clouds)):
            if self.clouds[cloud_idx][1] <= -48:
                self.clouds[cloud_idx] = ""

        while "" in self.clouds:
            self.clouds.remove("")

        # Reset the timers
        self.timer %= self.CLOUD_CREATION_COOLDOWN
        self.cloud_move_timer %= self.CLOUD_MOVE_COOLDOWN


register_effect("default:pale-clouds", PaleClouds)


class NeonEnvironmentDirt(Dirt):
    def __init__(self):
        super().__init__()
        self.image = FarmAssets.neon_dirt.copy()

    def update(self, player, pressed_keys, pickup_ready, farm):
        # Prevent duplication
        effect_count = 0
        for effect in farm.effects:
            if effect.__class__ == self.__class__:
                effect_count += 1

        if effect_count >= 2 and self.destruct_cd <= 0:
            farm.effects.remove(self)

        # Destruction timer
        if farm.environment == "default:neon":
            self.destruct_cd = 255
        else:
            if self.destruct_cd <= 0:
                farm.effects.remove(self)

            self.destruct_cd -= 3

        # Opacity
        self.opacity += 3


register_effect("default:neon-dirt", NeonEnvironmentDirt)


class NeonFireflies:
    def __init__(self):
        self.opacity = 0

        self.x = 108
        self.y = 96

        self.angle = 45
        self.x_vel = random.uniform(-1, 1)
        self.y_vel = (1 - self.x_vel ** 2) ** 0.5 * random.choice([-1, 1])

        self.img = pygame.surface.Surface((4, 4), pygame.SRCALPHA)

        # Prevent the hex from being spell checked
        # noinspection SpellCheckingInspection
        self.img.fill(random.choice(["#ff3b94", "#4deeea", "#74ee15", "#ffe700"]))

        self.just_created = True

    def blit(self, farm):
        firefly_count = 0
        for effect in farm.effects:
            if effect.__class__ == self.__class__:
                firefly_count += 1

        if self.just_created and firefly_count > 10:
            farm.effects[farm.effects.index(self)] = ""

        else:
            self.just_created = False
            screens["centered_display"].blit(self.img, ((farm.x + self.x) // 4 * 4, (248 + self.y) // 4 * 4))

    def update(self, player, pressed_keys, pickup_ready, farm):
        # TODO: Give this a custom animation for switching out of the environment
        if self.x <= 16:
            self.x_vel = random.uniform(0.5, 1)
            self.y_vel = (1 - self.x_vel ** 2) ** 0.5 * random.choice([-1, 1])

        if self.x >= 176:
            self.x_vel = random.uniform(-1, -0.5)
            self.y_vel = (1 - self.x_vel ** 2) ** 0.5 * random.choice([-1, 1])

        if self.y <= 32:
            self.y_vel = random.uniform(0.5, 1)
            self.x_vel = (1 - self.y_vel ** 2) ** 0.5 * random.choice([-1, 1])
        if self.y >= 200:
            self.y_vel = random.uniform(-1, -0.5)
            self.x_vel = (1 - self.y_vel ** 2) ** 0.5 * random.choice([-1, 1])

        self.x += self.x_vel * 2
        self.y += self.y_vel * 2
        # 224 248
        # 416 464
        # 192 216


register_effect("default:neon-fireflies", NeonFireflies)
