import pygame
from scripts.assets import RoomAssets

room_decoration = []


def register(pygame_module, clock_, **surfaces):
    global pygame
    global clock
    global screens

    pygame = pygame_module
    clock = clock_
    screens = surfaces


class Decoration:
    def __init__(self, x, y):
        # This class mainly exists so that if new functionality that affects all decorations is created it's easy to add
        self.x = round(x / 4) * 4
        self.y = round(y / 4) * 4
        self.image = RoomAssets.pod_light

    def update(self):
        pass

    def blit(self):
        screens["centered_display"].blit(self.image, (self.x, self.y))


# TODO: Animate the lights and give them parameters like how rain world handles objects in dev tools
class PodLights(Decoration):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = RoomAssets.pod_light
        self.light = RoomAssets.pod_light_lux

    def blit(self):
        # Blit the image with light overlaid
        screens["centered_display"].blit(self.image, (self.x, self.y))
        screens["light_display"].blit(self.light, (self.x, self.y), special_flags=pygame.BLEND_RGB_ADD)


# 144
# 964
room_decoration.append(PodLights(144 + 0 * 241 - 18, 200))
room_decoration.append(PodLights(144 + 1 * 241 - 18, 200))
room_decoration.append(PodLights(144 + 2 * 241 - 18, 200))
room_decoration.append(PodLights(144 + 3 * 241 - 18, 200))
