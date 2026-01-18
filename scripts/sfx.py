import os
import pygame

pygame.init()
pygame.mixer.init()

class SFX:
    pass

class SFXDispenser:
    select = pygame.mixer.Sound(os.path.join("sfx", "select.mp3"))
    switch = pygame.mixer.Sound(os.path.join("sfx", "switch.mp3"))
    switch.set_volume(0.1)
