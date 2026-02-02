import os
import pygame

pygame.init()
pygame.mixer.init()


class SFX:
    pass


class SFXDispenser:
    select = pygame.mixer.Sound(os.path.join("sfx", "dispenser", "select.mp3"))

    switch = pygame.mixer.Sound(os.path.join("sfx", "dispenser", "switch.mp3"))
    switch.set_volume(0.1)

    zap = pygame.mixer.Sound(os.path.join("sfx", "dispenser", "zap.mp3"))

    # Temporary placeholder for a notification sound that plays when an item is fabricated
    fabricated = pygame.mixer.Sound(os.path.join("sfx", "dispenser", "fabricated.mp3"))
