import pygame
import os


# This is used as a variable storage medium in a way similar to assets
class Fonts:
    pygame.font.init()
    default_font = pygame.font.Font(os.path.join("font", "outer-font.ttf"), 32)
