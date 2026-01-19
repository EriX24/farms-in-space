# TODO: investigate why the pale bush item is shifted on the first use
import copy
import ctypes
import math
import os
import random

import pygame
import sys

# Scripts
from scripts.assets import Assets
from scripts.assets import ItemAssets
from scripts.assets import DispenserAssets
from scripts.assets import GeneratorAssets
from scripts.assets import FarmAssets
from scripts.assets import PlayerAssets
from scripts.assets import RoomAssets
from scripts.assets import KeyAssets
from scripts.logger import log_error

from scripts.sfx import SFXDispenser

from scripts.recipes import RecipeManager
from scripts.recipes import EnvironmentRecipeManager

from scripts import items_register
from scripts import plants_register
from scripts import farms as farm_creator
from scripts import environment_effects

# Pygame init
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((1400, 800), pygame.RESIZABLE)
display = pygame.surface.Surface((1400, 800), pygame.SRCALPHA)
centered_display = pygame.surface.Surface((1400, 800), pygame.SRCALPHA)
overlay = pygame.surface.Surface((1400, 800), pygame.SRCALPHA)
clock = pygame.time.Clock()
pygame.display.set_caption("Outer")

items_register.register(pygame, clock, screen=screen, display=display, centered_display=centered_display,
                        overlay=overlay)

plants_register.register(pygame, clock, screen=screen, display=display, centered_display=centered_display,
                         overlay=overlay)

farm_creator.register(pygame, clock, screen=screen, display=display, centered_display=centered_display,
                      overlay=overlay)

environment_effects.register(pygame, clock, screen=screen, display=display, centered_display=centered_display,
                             overlay=overlay)

recipe_manager = RecipeManager()
environment_recipe_manager = EnvironmentRecipeManager()

# Game vars
mode = "menu"  # "setup", "menu" and "play"
mouse_lifted = True
j_ready = True
l_ready = True
k_ready = True
dev_tools = True
glitch_effects = False
enhanced_glitch_effects = False

pickup_items = {}
items = []

# Menu vars
stars = []

# Item assets
test_leaf = ItemAssets.test_leaf
item_assets = {}

# Ui assets
title = Assets.title

# Dev tools assets
spacebar_command = Assets.spacebar_command
o_command = Assets.o_command
i_command = Assets.i_command
l_command = Assets.l_command

# Menu assets
play_button_dark = Assets.play_button_dark
play_button_lit = Assets.play_button_lit
glitch_effect_off = Assets.glitch_effect_off
glitch_effect_on = Assets.glitch_effect_on

shooting_star_1 = Assets.shooting_star_1
shooting_star_2 = Assets.shooting_star_2
shooting_star_3 = Assets.shooting_star_3

# Glitch effects [PRIMARY]
energy_depleting_text = Assets.energy_depleting_text

# Glitch effects [SECONDARY]
energy_depleting_glitching = Assets.energy_depleting_glitching

# Buttons
play_button_rect = play_button_lit.get_rect()

# Toggles
glitch_toggle_rect = glitch_effect_on.get_rect()

# OST
ost_authorised = pygame.mixer.Sound(os.path.join("ost", "authorised.mp3"))
ost_danger = pygame.mixer.Sound(os.path.join("ost", "danger.mp3"))

# Letter display reference
number_ref = {"0": KeyAssets.number_0,
              "1": KeyAssets.number_1,
              "2": KeyAssets.number_2,
              "3": KeyAssets.number_3,
              "4": KeyAssets.number_4,
              "5": KeyAssets.number_5,
              "6": KeyAssets.number_6,
              "7": KeyAssets.number_7,
              "8": KeyAssets.number_8,
              "9": KeyAssets.number_9,
              ".": KeyAssets.decimal}

# Item frame ref
item_frame_ref = {"bottom-left": DispenserAssets.item_frame_bottom_left,
                  "bottom-right": DispenserAssets.item_frame_bottom_right,
                  "top-left": DispenserAssets.item_frame_top_left,
                  "top-right": DispenserAssets.item_frame_top_right}

# Dispenser entries
entries = ["storage", "fabricate", "drones", "processes", "farms"]

# Farm update ticks
FARM_UPDATE_TICKS = 500
plants_register.FARM_UPDATE_TICKS = FARM_UPDATE_TICKS


# (22, 558)
# (1177, 201)

# Test plant

# plant = plants_register.Plant(236, "pale")


# Hologram creator
class Holograms:
    def __init__(self):
        self.holograms = {}

    @staticmethod
    def quick_hologram(display_surface, hologram: pygame.surface.Surface, loc: tuple[int, int], alpha=100):
        hologram.set_alpha(alpha)
        display_surface.blit(hologram, loc)

    def create_hologram(self, hologram: pygame.surface.Surface, alpha: int, hologram_id: str):
        if self.holograms.get(hologram_id, None) is None:
            hologram.set_alpha(alpha)
            self.holograms[hologram_id] = hologram
        else:
            raise ValueError("There is a hologram with the same id")

    def load_hologram(self, display_surface: pygame.surface.Surface, hologram_id, loc: tuple[int, int]):
        display_surface.blit(self.holograms[hologram_id], loc)


# Dispenser class
class Dispenser:
    def __init__(self):
        # Assets
        self.assets = DispenserAssets

        # Rect
        self.rect = self.assets.dispenser_closed.get_rect()
        self.rect.x = 1180
        self.rect.y = 200

        # Accessory area
        self.accessory_rect = self.assets.dispenser_energy_pipes.get_rect()
        self.accessory_rect.x = 1060
        self.accessory_rect.y = 200

        # Dispenser
        self.open = False
        self.shelf_mode = 0
        self.shelf_items = []
        self.open_ticks = 0
        self.history = ["unselected"]  # What it will go to when you press L

        # Items
        self.stored_items = {"pale-air": 50, "pale-argon": 50, "pale-moss-swathe": 6,
                             "light-bulb-fern-seed": 5, "pale-bush-seed": 5, "energy-leaf": 0}

        # Items being fabricated
        self.fabricating_items = []

        # Fabrication frame stats
        self.frame_lit_ticks = 0
        self.frame_lit_duration = 125
        self.fabrication_frame_red = False

        # How open the screen is
        self.screen_mode = 3

        # Screen
        self.dispenser_screen = pygame.surface.Surface((160, 204))
        self.screen_rect = self.assets.dispenser_screen_off.get_rect()
        self.screen_rect.x = 1200
        self.screen_rect.y = 220

        # Options info
        self.entry = "unselected"
        self.lit_option = "storage"

        # Keys
        self.a_pressed = 0
        self.d_pressed = 0

        # Currently selected
        self.current_item = 0
        self.current_recipe = 0
        self.current_environment_recipe = 0
        self.current_farm = 0
        self.farms_selection_selected = True
        self.farms_mode = "items"

        # Misc
        self.progress = 0  # How much the items have been processed on the shelf
        self.arrow_hold_ticks = 100  # How long arrows hold down for

    def blit(self):
        # Blit every item on the shelf
        for item_ in self.shelf_items:
            centered_display.blit(item_.image, ((1120 + item_.progress * 4) // 4 * 4,
                                                (424 - item_.image.get_height()) // 4 * 4),
                                  (0, 0, (60 - (item_.progress * 4)), item_.image.get_height()))

        # Display the dispenser
        if self.open:
            centered_display.blit(self.assets.dispenser_open, self.rect)
        else:
            centered_display.blit(self.assets.dispenser_closed, self.rect)

        # Decoration
        centered_display.blit(self.assets.dispenser_energy_pipes, self.accessory_rect)

        # Shelf
        if self.shelf_mode <= 1:
            centered_display.blit(self.assets.dispenser_shelf_up, self.accessory_rect)
        elif self.shelf_mode <= 2:
            centered_display.blit(self.assets.dispenser_shelf_transition, self.accessory_rect)
        else:
            centered_display.blit(self.assets.dispenser_shelf_down, self.accessory_rect)

        # Dispenser screen
        self.screen_blit()

    def update(self):
        # Dispenser door
        if pressed_keys[pygame.K_SPACE] and dev_tools:
            self.open_ticks = 100
            self.open = True
        else:
            self.open = False

        # Process items
        self.progress += clock.get_time()

        for item_ in self.shelf_items:
            if item_.progress >= 15:
                # If the item is no longer visible, put it in storage
                self.shelf_items.remove(item_)

                if not self.stored_items.get(item_.name, False):
                    # If the item hasn't been discovered yet (doesn't have an entry in storage)
                    item_list_pre = list(self.stored_items)
                    item_list_pre.sort()

                    self.stored_items[item_.name] = 1

                    previous_item_name = item_list_pre[self.current_item]

                    item_list_post = list(self.stored_items)
                    item_list_post.sort()

                    self.current_item = item_list_post.index(previous_item_name)
                else:
                    # If the item has already been discovered (has an entry in storage)
                    self.stored_items[item_.name] += 1

            # Progress visible items
            item_.progress += self.progress // 100

            del item_

        # Refactor/modulo self.progress
        self.progress %= 100

        # Dispenser shelf
        if player.rect.x >= 1000:
            self.shelf_mode += 0.3

            if self.shelf_mode > 3:
                self.shelf_mode = 3
        else:
            self.shelf_mode -= 0.3

            if self.shelf_mode < 0:
                self.shelf_mode = 0

        # Force the shelf to be up it there are items
        if self.shelf_items:
            self.shelf_mode = 3

        # Dispenser flap
        if self.open_ticks > 0:
            self.open_ticks -= clock.get_time()

        if self.open_ticks < 0:
            self.open_ticks = 0

        if self.open_ticks > 0:
            self.open = True
        else:
            self.open = False

        # Dispenser screen
        if player.rect.x >= 1000:
            self.screen_mode -= 0.1

        if self.screen_mode > 3:
            self.screen_mode = 3

        if self.screen_mode < 0:
            self.screen_mode = 0

        # History
        if not self.history:
            self.history = ["unselected"]

        # Update the screen
        self.screen_update()

    def que_item(self, item_):
        """Place a new item onto the shelf"""
        item_.progress = 0
        self.shelf_items.append(item_)

    def switch_entry(self, entry):
        self.entry = entry
        self.history.append(entry)
        print(self.entry)

    def screen_blit(self):
        """Blit what's on the screen"""
        # Screen base
        centered_display.blit(self.assets.dispenser_screen_off, (1200, 220))
        self.dispenser_screen.blit(self.assets.dispenser_screen_on, (0, 0))

        # No entry selected
        if self.entry == "unselected":
            # Show the options
            self.dispenser_screen.blit(self.assets.storage_option_dark, (0, 0))
            self.dispenser_screen.blit(self.assets.fabricate_option_dark, (0, 0))
            self.dispenser_screen.blit(self.assets.drones_option_dark, (0, 0))
            self.dispenser_screen.blit(self.assets.processes_option_dark, (0, 0))
            self.dispenser_screen.blit(self.assets.farms_option_dark, (0, 0))

            # Show which entry is highlighted if the player is connected
            if player.dispenser_selected:
                self.dispenser_screen.blit({"storage": self.assets.storage_option_lit,
                                            "fabricate": self.assets.fabricate_option_lit,
                                            "drones": self.assets.drones_option_lit,
                                            "processes": self.assets.processes_option_lit,
                                            "farms": self.assets.farms_option_lit}[self.lit_option], (0, 0))

        # Storage selected
        elif self.entry == "storage":
            # Title card
            self.dispenser_screen.blit(self.assets.storage_entry, (0, 0))

            # Item list
            item_list_ = list(self.stored_items.keys())
            item_list_.sort()

            # Display the stored item
            if item_list_:
                # Normalise index
                self.current_item %= len(item_list_)

                # Item texture
                item_image = items_register.item_image_ref[item_list_[self.current_item]]

                # Show the frame for the item
                self.dispenser_screen.blit(item_frame_ref["top-left"], (4, 36))
                self.dispenser_screen.blit(item_frame_ref["top-right"], (12 + item_image.get_width(), 36))
                self.dispenser_screen.blit(item_frame_ref["bottom-left"], (4, 44 + item_image.get_height()))
                self.dispenser_screen.blit(item_frame_ref["bottom-right"],
                                           (12 + item_image.get_width(), 44 + item_image.get_height()))

                # Show the item
                self.dispenser_screen.blit(item_image, (12, 44))

                # Show the amount of the item
                amount = str(self.stored_items[item_list_[self.current_item]]).split(".")
                if len(amount) == 2:
                    amount[-1] = amount[-1][:3]
                    amount = ".".join(amount)

                else:
                    amount = amount[0]

                for number_idx in range(len(amount)):
                    number = str(self.stored_items[item_list_[self.current_item]])[number_idx]
                    self.dispenser_screen.blit(number_ref[number],
                                               (number_idx * 16,
                                                52 + item_image.get_height()))

                del item_image

            # Arrow keys
            if player.dispenser_selected:
                if self.a_pressed:
                    # 1256 400
                    # 1200 220
                    self.dispenser_screen.blit(self.assets.left_arrow_lit, (56, 180))
                else:
                    self.dispenser_screen.blit(self.assets.left_arrow, (56, 180))

                if self.d_pressed:
                    # 1288 400
                    self.dispenser_screen.blit(self.assets.right_arrow_lit, (88, 180))
                else:
                    self.dispenser_screen.blit(self.assets.right_arrow, (88, 180))

            else:
                self.dispenser_screen.blit(self.assets.left_arrow, (56, 180))
                self.dispenser_screen.blit(self.assets.right_arrow, (88, 180))

        # Fabrication selected
        elif self.entry == "fabricate":
            # Title card
            self.dispenser_screen.blit(self.assets.fabricate_entry, (0, 0))

            # Restore to the default colour after a while
            if self.frame_lit_ticks < 0:
                self.frame_lit_ticks = 0
                self.fabrication_frame_red = False
            else:
                self.frame_lit_ticks -= clock.get_time()

            # Colour of the frame, depending on the action
            if self.frame_lit_ticks > 0:
                # Lit frame
                self.dispenser_screen.blit({True: self.assets.red_frame,
                                            False: self.assets.lit_frame}[self.fabrication_frame_red], (0, 0))
            else:
                # Unlit frame
                self.dispenser_screen.blit(self.assets.unlit_frame, (0, 0))

            # Current recipe
            self.dispenser_screen.blit(
                recipe_manager.recipes[list(recipe_manager.recipes.keys())[self.current_recipe]]["blueprint"], (0, 0))

            # Arrow keys
            if player.dispenser_selected:
                if self.a_pressed:
                    # 1204 348
                    # 1200 216
                    self.dispenser_screen.blit(self.assets.left_arrow_lit, (4, 128))
                else:
                    self.dispenser_screen.blit(self.assets.left_arrow, (4, 128))

                if self.d_pressed:
                    self.dispenser_screen.blit(self.assets.right_arrow_lit, (140, 128))
                else:
                    self.dispenser_screen.blit(self.assets.right_arrow, (140, 128))

            else:
                self.dispenser_screen.blit(self.assets.left_arrow, (4, 128))
                self.dispenser_screen.blit(self.assets.right_arrow, (140, 128))

        # Drones selected
        elif self.entry == "drones":
            # WIP
            self.dispenser_screen.blit(self.assets.drones_entry, (0, 0))
            self.dispenser_screen.blit(self.assets.wip, (0, 0))

        # Processes selected
        elif self.entry == "processes":
            # Title card
            self.dispenser_screen.blit(self.assets.processes_entry, (0, 0))

            # Fabrication progress
            for item_idx in range(len(self.fabricating_items[:6])):
                value = self.fabricating_items[item_idx]
                if value != "FABRICATED":
                    # Loading bar
                    pygame.draw.rect(self.dispenser_screen, "#FFFF00",
                                     (8, 40 + (item_idx * 24),
                                      (144 * (value[list(value.keys())[0]] / value["total"])) // 4 * 4, 8))

                del item_idx

            # Show the processes bars
            self.dispenser_screen.blit(self.assets.fabrication_1, (0, 0))
            self.dispenser_screen.blit(self.assets.fabrication_2, (0, 0))
            self.dispenser_screen.blit(self.assets.fabrication_3, (0, 0))
            self.dispenser_screen.blit(self.assets.fabrication_4, (0, 0))
            self.dispenser_screen.blit(self.assets.fabrication_5, (0, 0))
            self.dispenser_screen.blit(self.assets.fabrication_6, (0, 0))

        # Farms selected
        elif self.entry == "farms":
            # WIP
            # TODO: Work on the accessing of the farms
            self.dispenser_screen.blit(self.assets.farms_entry, (0, 0))
            self.dispenser_screen.blit(self.assets.farm_selection, (0, 0))

            item_list_ = list(self.stored_items)
            item_list_.sort()

            if self.farms_selection_selected:
                self.dispenser_screen.blit(self.assets.farms_selection_selected, (0, 0))

            self.dispenser_screen.blit(self.assets.switch_entry, (0, 0))
            self.dispenser_screen.blit(self.assets.plant_key, (0, 0))

            self.dispenser_screen.blit(self.assets.farms_frame_unlit, (4, 92))  # Items

            if self.stored_items[item_list_[self.current_item]] == 0 or not items_register.items_ref.get(
                    item_list_[self.current_item]).plantable:
                self.dispenser_screen.blit(self.assets.farms_frame_red_x, (4, 92))

            if self.farms_mode == "items" and not self.farms_selection_selected:
                self.dispenser_screen.blit(self.assets.farms_frame_lit, (4, 92))

                if self.stored_items[item_list_[self.current_item]] == 0:
                    self.dispenser_screen.blit(self.assets.farms_frame_red_x, (4, 92))

            self.dispenser_screen.blit(self.assets.farms_frame_unlit, (84, 92))  # Environment
            if self.farms_mode == "environment" and not self.farms_selection_selected:
                self.dispenser_screen.blit(self.assets.farms_frame_lit, (84, 92))

            item_display_rect = self.assets.farms_frame_lit.get_rect()
            item_display_rect.x = 4
            item_display_rect.y = 92

            item_rect = items_register.item_image_ref[item_list_[self.current_item]].get_rect()
            item_rect.center = [round(item_display_rect.center[0] / 4) * 4, round(item_display_rect.center[1] / 4) * 4]

            self.dispenser_screen.blit(items_register.item_image_ref[item_list_[self.current_item]], item_rect)
            del item_list_
            del item_rect
            del item_display_rect

            self.dispenser_screen.blit(self.assets.selected_farm, (4 + 40 * self.current_farm, 36))

        elif self.entry == "environment":
            # Restore to the default colour after a while
            if self.frame_lit_ticks < 0:
                self.frame_lit_ticks = 0
            else:
                self.frame_lit_ticks -= clock.get_time()

            self.dispenser_screen.blit(self.assets.environment_entry)

            environments = list(environment_recipe_manager.recipes.keys())
            environments.sort()

            self.dispenser_screen.blit(
                environment_recipe_manager.recipes[environments[self.current_environment_recipe]]["blueprint"], (0, 0))

            if self.frame_lit_ticks > 0:
                self.dispenser_screen.blit(self.assets.lit_environment_frame, (0, 0))

            del environments

        else:
            # Four04
            self.dispenser_screen.blit(self.assets.four04, (0, 0))

        # Special
        if player.dispenser_selected:
            self.dispenser_screen.blit(self.assets.connected_symbol, (0, 0))

            if self.entry == "storage":
                # Controls
                self.dispenser_screen.blit(self.assets.control_drop, (0, 0))

        # Show the screen
        centered_display.blit(self.dispenser_screen, (1200, 220 + (34 * self.screen_mode) // 4 * 4),
                              (0, 0 + (34 * self.screen_mode) // 4 * 4, 160,
                               (102 - (34 * self.screen_mode)) * 2 // 4 * 4))

    def screen_update(self):
        if player.dispenser_selected:
            # Storage selected
            if self.entry == "storage":
                # Arrow symbols
                if pressed_keys[pygame.K_a] and player.a_ready:
                    self.a_pressed = self.arrow_hold_ticks
                    self.current_item -= 1

                    # "switch.mp4" sound effect
                    SFXDispenser.switch.play()

                elif pressed_keys[pygame.K_a] and not player.a_ready:
                    if self.a_pressed > 0:
                        self.a_pressed -= clock.get_time()

                    if self.a_pressed < 0:
                        self.a_pressed = 0
                else:
                    self.a_pressed = 0

                if pressed_keys[pygame.K_d] and player.d_ready:
                    self.d_pressed = self.arrow_hold_ticks
                    self.current_item += 1

                    # "switch.mp4" sound effect
                    SFXDispenser.switch.play()

                elif pressed_keys[pygame.K_d] and not player.d_ready:
                    if self.d_pressed > 0:
                        self.d_pressed -= clock.get_time()

                    if self.d_pressed < 0:
                        self.d_pressed = 0
                else:
                    self.d_pressed = 0

                # Dispense items
                if pressed_keys[pygame.K_k] and k_ready:
                    # Item list
                    item_list = list(self.stored_items.keys())
                    item_list.sort()

                    # If there are items...
                    # print(items_register.items_ref[item_list[self.current_item]].dispensable)
                    if item_list and items_register.items_ref[item_list[self.current_item]].dispensable:
                        # Get the class of the current item
                        item_class = items_register.items_ref[item_list[self.current_item]]

                        # Get a random x value to spawn the item at
                        if 1340 - items_register.item_image_ref[item_list[self.current_item]].get_width() >= 1220:
                            x_ = random.randint(1220, 1340 - items_register.item_image_ref[
                                item_list[self.current_item]].get_width())
                        else:
                            x_ = 1220

                        # New item object
                        new_item = item_class(x_, 516 - items_register.item_image_ref[
                            item_list[self.current_item]].get_height(), True)

                        # If the player has at least one of the item...
                        if self.stored_items[new_item.name] >= 1:
                            # Spawn the item
                            items.append(new_item)

                            # Deduct one item
                            self.stored_items[new_item.name] -= 1

                            # Open the dispenser
                            self.open_ticks = 500

                            # Play SFX
                            SFXDispenser.select.play()

                        # if self.stored_items[new_item.name] <= 0:
                        #     self.stored_items.pop(new_item.name)

                        del new_item
                        del x_
                        del item_class

            elif self.entry == "fabricate":
                # print(self.current_recipe)

                if pressed_keys[pygame.K_a] and player.a_ready:
                    self.a_pressed = self.arrow_hold_ticks
                    self.current_recipe -= 1
                    SFXDispenser.switch.play()

                elif pressed_keys[pygame.K_a] and not player.a_ready:
                    if self.a_pressed > 0:
                        self.a_pressed -= clock.get_time()

                    if self.a_pressed < 0:
                        self.a_pressed = 0
                else:
                    self.a_pressed = 0

                if pressed_keys[pygame.K_d] and player.d_ready:
                    self.d_pressed = self.arrow_hold_ticks
                    self.current_recipe += 1
                    SFXDispenser.switch.play()

                elif pressed_keys[pygame.K_d] and not player.d_ready:
                    if self.d_pressed > 0:
                        self.d_pressed -= clock.get_time()

                    if self.d_pressed < 0:
                        self.d_pressed = 0
                else:
                    self.d_pressed = 0

                # Fabricate a item
                if pressed_keys[pygame.K_k] and k_ready:
                    item_recipe = recipe_manager.recipes[list(recipe_manager.recipes.keys())[self.current_recipe]]

                    enough_materials = True
                    for item_required in item_recipe["input"]:
                        if item_recipe["input"][item_required] <= self.stored_items.get(item_required, 0):
                            enough_materials = True
                        else:
                            enough_materials = False
                            break

                    if enough_materials:
                        print("OK")
                        self.frame_lit_ticks = self.frame_lit_duration

                        for item_required in item_recipe["input"]:
                            self.stored_items[item_required] -= item_recipe["input"][item_required]

                        time = item_recipe["time"]
                        if type(time) == list:
                            time = random.randint(time[0], time[1])

                        self.fabricating_items.append({item_recipe["id"]: time, "total": time})

                        del time
                    else:
                        self.frame_lit_ticks = self.frame_lit_duration
                        self.fabrication_frame_red = True

                    del enough_materials
                    del item_recipe

            elif self.entry == "farms":
                if pressed_keys[pygame.K_a] and player.a_ready:
                    self.a_pressed = self.arrow_hold_ticks

                    if self.farms_selection_selected:
                        self.current_farm -= 1
                    else:
                        self.farms_mode = {"items": "environment", "environment": "items"}[self.farms_mode]

                    SFXDispenser.switch.play()

                elif pressed_keys[pygame.K_a] and not player.a_ready:
                    if self.a_pressed > 0:
                        self.a_pressed -= clock.get_time()

                    if self.a_pressed < 0:
                        self.a_pressed = 0
                else:
                    self.a_pressed = 0

                if pressed_keys[pygame.K_d] and player.d_ready:
                    self.d_pressed = self.arrow_hold_ticks

                    if self.farms_selection_selected:
                        self.current_farm += 1
                    else:
                        self.farms_mode = {"items": "environment", "environment": "items"}[self.farms_mode]

                    SFXDispenser.switch.play()

                elif pressed_keys[pygame.K_d] and not player.d_ready:
                    if self.d_pressed > 0:
                        self.d_pressed -= clock.get_time()

                    if self.d_pressed < 0:
                        self.d_pressed = 0
                else:
                    self.d_pressed = 0

                if pressed_keys[pygame.K_s] and player.s_ready:
                    self.farms_selection_selected = False
                    self.farms_mode = "items"

                    SFXDispenser.switch.play()

                if pressed_keys[pygame.K_w] and player.w_ready:
                    self.farms_selection_selected = True

                    SFXDispenser.switch.play()

                # Plant an item
                if pressed_keys[pygame.K_k] and k_ready:
                    item_list_ = list(self.stored_items)
                    item_list_.sort()
                    # print(items_register.items_ref[item_list_[self.current_item]], "start")
                    #
                    current_item_ = items_register.items_ref[item_list_[self.current_item]]
                    #
                    if current_item_.plantable:
                        current_farm = [farms.farm_1, farms.farm_2, farms.farm_3, farms.farm_4][self.current_farm]
                        new_plant_class = plants_register.plant_ref[current_item_.plant]
                        new_plant = new_plant_class(current_farm.x + random.randint(0, 196) // 4 * 4,
                                                    current_farm.environment)

                        print("item2")
                        current_farm.add_plant(new_plant)

                item_list_ = list(self.stored_items)
                item_list_.sort()

                # current_farm.plants = plants_copy
                # print(items_register.items_ref[item_list_[self.current_item]], "finish")

                if pressed_keys[
                    pygame.K_j] and j_ready and not self.farms_selection_selected and self.farms_mode == "items":
                    self.switch_entry("storage")
                    SFXDispenser.select.play()

                if pressed_keys[
                    pygame.K_j] and j_ready and not self.farms_selection_selected and self.farms_mode == "environment":
                    self.switch_entry("environment")

                    environments = list(environment_recipe_manager.recipes.keys())
                    environments.sort()

                    current_environment = [farms.farm_1, farms.farm_2, farms.farm_3, farms.farm_4][
                        self.current_farm].environment
                    self.current_environment_recipe = environments.index(
                        [environment_recipe_manager.recipes[recipe] for recipe in environments if
                         environment_recipe_manager.recipes[recipe]["environment"] == current_environment][0]["id"])

                    SFXDispenser.select.play()


            elif self.entry == "environment":
                if pressed_keys[pygame.K_a] and player.a_ready:
                    self.a_pressed = self.arrow_hold_ticks
                    self.current_environment_recipe -= 1
                    self.frame_lit_ticks = 0

                    SFXDispenser.switch.play()

                elif pressed_keys[pygame.K_a] and not player.a_ready:
                    if self.a_pressed > 0:
                        self.a_pressed -= clock.get_time()

                    if self.a_pressed < 0:
                        self.a_pressed = 0
                else:
                    self.a_pressed = 0

                if pressed_keys[pygame.K_d] and player.d_ready:
                    self.d_pressed = self.arrow_hold_ticks
                    self.current_environment_recipe += 1
                    self.frame_lit_ticks = 0

                    SFXDispenser.switch.play()

                elif pressed_keys[pygame.K_d] and not player.d_ready:
                    if self.d_pressed > 0:
                        self.d_pressed -= clock.get_time()

                    if self.d_pressed < 0:
                        self.d_pressed = 0
                else:
                    self.d_pressed = 0

                if pressed_keys[pygame.K_k] and k_ready:
                    self.frame_lit_ticks = self.frame_lit_duration

                    environments = list(environment_recipe_manager.recipes.keys())
                    environments.sort()

                    current_selected_environment = \
                        environment_recipe_manager.recipes[environments[self.current_environment_recipe]]["environment"]

                    [farms.farm_1, farms.farm_2, farms.farm_3, farms.farm_4][
                        self.current_farm].environment = current_selected_environment
                    [farms.farm_1, farms.farm_2, farms.farm_3, farms.farm_4][self.current_farm].effects_added = False

                    SFXDispenser.select.play()

        # Make the current variables rotate when it goes to low or too high
        if self.stored_items.keys():
            self.current_item %= len(self.stored_items.keys())

        # Prevent the index from going above the limit
        self.current_recipe %= len(recipe_manager.recipes.keys())
        self.current_farm %= 4
        self.current_environment_recipe %= len(environment_recipe_manager.recipes.keys())

        # Process an item
        for item_ in range(len(self.fabricating_items)):
            if item_ <= 5:
                if self.fabricating_items[item_] != "FABRICATED":
                    # Get the time it takes for the item to be finished
                    item_value = self.fabricating_items[item_][list(self.fabricating_items[item_].keys())[0]]

                    # Get the .json file the recipy came from
                    item_recipe = recipe_manager.recipes[list(self.fabricating_items[item_].keys())[0]]

                    if item_value > 0:
                        # Deduct the remaining time before the item gets fabricated
                        self.fabricating_items[item_][
                            list(self.fabricating_items[item_].keys())[0]] -= clock.get_time()
                    else:
                        # If the remaining time is below or equal to zero, fabricate it
                        self.fabricating_items[item_] = "FABRICATED"

                        output_items = []
                        # item_ * output_ for output_ in item_recipe["output"] for item_ in output_

                        for output_ in item_recipe["output"]:
                            # chance_output_items = []
                            # for item__ in item_recipe["output"].keys():
                            #     for i in range(len(list(item_recipe["output"][item__].keys()))):
                            #         chance_output_items.append(item_recipe["output"][item__])
                            for j in range(output_["weight"]):
                                output_items.append(output_["items"])

                            # output_items.append(chance_output_items)

                        selected_output = random.choice(output_items)
                        for new_item in selected_output:
                            if type(selected_output[new_item]) == list:
                                amount = random.randint(selected_output[new_item][0], selected_output[new_item][1])

                                if self.stored_items.get(new_item):
                                    self.stored_items[new_item] += amount
                                else:
                                    self.stored_items[new_item] = amount
                            else:
                                if self.stored_items.get(new_item):
                                    self.stored_items[new_item] += selected_output[new_item]
                                else:
                                    self.stored_items[new_item] = selected_output[new_item]

                        # for new_item_name in output:
                        #     if self.stored_items.get(new_item_name):
                        #         self.stored_items[new_item_name] += 1
                        #     else:
                        #         self.stored_items[new_item_name] = 1

                        """Other old code
                        # How much "chance" exists in total across all possible outputs
                        total_chance = sum(
                            [item_recipe["output"][item_out]["chance"] for item_out in item_recipe["output"]])

                        # Which item should it truly output
                        output_item = random.randint(1, total_chance)
                        current_chance = 0

                        for item_out in item_recipe["output"]:
                            # Increase the current "chance" value it's on
                            current_chance += item_recipe["output"][item_out]["chance"]

                            # If the current chance value is higher create that item
                            if current_chance >= output_item:
                                output += [item_out] * item_recipe["output"][item_out]["amount"]

                        for new_item_name in output:
                            if self.stored_items.get(new_item_name):
                                self.stored_items[new_item_name] += 1
                            else:
                                self.stored_items[new_item_name] = 1
                        """

                        """ Old Code
                        # Open the dispenser
                        self.open_ticks = 500
        
                        for new_item_name in output:
                            # Get a random x position near the chute
                            if 1340 - items_register.item_image_ref[new_item_name].get_width() >= 1220:
                                x_ = random.randint(1220,
                                                    1340 - items_register.item_image_ref[
                                                        new_item_name].get_width())
                            else:
                                x_ = 1220
        
                            # Spawn the item
                            new_item = (items_register.items_ref[new_item_name]
                                        (x_, 516 - items_register.item_image_ref[new_item_name].get_height(),
                                         True))
        
                            items.append(new_item)
                        """

                        del item_

            else:
                # If it's not in the first 6 prosecutable items, break the loop
                break

        # Remove all fabricated entries
        if len(self.fabricating_items) > 6:
            while "FABRICATED" in self.fabricating_items:
                self.fabricating_items.remove("FABRICATED")
        else:
            if len([item_ for item_ in self.fabricating_items if item_ == "FABRICATED"]) == len(self.fabricating_items):
                self.fabricating_items = []


# Generator class
class Generator:
    def __init__(self):
        self.assets = GeneratorAssets

        self.rect = self.assets.generator_default.get_rect()
        self.rect.x = 20
        self.rect.y = 200

    def blit(self):
        centered_display.blit(self.assets.generator_default, self.rect)

    def update(self):
        pass


# Farms class
class Farms:
    def __init__(self):
        self.assets = FarmAssets
        new_item = plants_register.LightBulbFern(408 - 60, "pale")
        self.farm_1 = farm_creator.Farm(224)
        self.farm_1.plants.append(new_item)

        # new_item = plants_register.PaleBushPlant(408 - 160, "pale")
        # self.farm_1.plants.append(new_item)

        new_item = plants_register.PaleMoss(408 - 160, "pale")
        self.farm_1.plants.append(new_item)

        # self.farm_1.environment = "pale"

        self.farm_2 = farm_creator.Farm(428)
        self.farm_3 = farm_creator.Farm(632)
        self.farm_4 = farm_creator.Farm(836)

        for farm_ in [self.farm_1, self.farm_2, self.farm_3, self.farm_4]:
            for effect in farm_.effects:
                if type(effect) == environment_effects.Grass:
                    pass
                    effect.layer_1_opacity = 255
                    effect.layer_1b_opacity = 255
                    effect.layer_2_opacity = 255
                    effect.layer_3_opacity = 255

                    effect.grow_layer()
                    effect.grow_layer()
                    effect.grow_layer()
                    effect.grow_layer()

        self.farm_1.environment = "pale"
        self.farm_1.effects_added = False

        self.progress = 0
        # Farm box pos: 224 248
        # Farm box pos: 428 248
        # Farm box pos: 632 248
        # Farm box pos: 836 248

    def blit(self):
        # Farm 1
        # centered_display.blit(self.assets.environment_overlay.get(self.farm_1["environment"], self.assets.blank_canvas),
        #                       (224, 248))
        #
        # centered_display.blit(self.assets.farm_box, (224, 248))
        #
        # # Farm 2
        # centered_display.blit(self.assets.environment_overlay.get(self.farm_2["environment"], self.assets.blank_canvas),
        #                       (428, 248))
        #
        # centered_display.blit(self.assets.farm_box, (428, 248))
        #
        # # Farm 3
        # centered_display.blit(self.assets.environment_overlay.get(self.farm_3["environment"], self.assets.blank_canvas),
        #                       (632, 248))
        #
        # centered_display.blit(self.assets.farm_box, (632, 248))
        #
        # # Farm 4
        # centered_display.blit(self.assets.environment_overlay.get(self.farm_4["environment"], self.assets.blank_canvas),
        #                       (836, 248))
        #
        # centered_display.blit(self.assets.farm_box, (836, 248))
        self.farm_1.blit()
        self.farm_2.blit()
        self.farm_3.blit()
        self.farm_4.blit()

    def update(self):
        self.progress += clock.get_time()

        if self.progress:
            print(self.progress)
            for _ in range(int(self.progress // FARM_UPDATE_TICKS)):
                for farm_object in [self.farm_1, self.farm_2, self.farm_3, self.farm_4]:
                    environment_req = \
                        [environment_recipe_manager.recipes[environment]["input"] for environment in
                         environment_recipe_manager.recipes
                         if environment_recipe_manager.recipes[environment]["environment"] == farm_object.environment][
                            0]

                    # for req_item in environment_req:
                    #     if (dispenser.stored_items.get(req_item) and
                    #             dispenser.stored_items.get(req_item) -
                    #             (environment_req[req_item] - farm["provided_items"].get(req_item, 0)) >= 0):
                    #
                    #     # elif farm["environment_items"].get(req_item, 0) >= environment_req[req_item]:
                    #     #     environment_sustained = True
                    #
                    #     else:
                    #         break

                    # Provide all resources first so no plant is treated unevenly when it checks if the plant should die
                    for plant_ in farm_object.plants:
                        plant_.evaluate_output(farm_object)

                    # Loop through the environments requirements
                    for req_item in environment_req:
                        required_item = environment_req[req_item] / (1000 / FARM_UPDATE_TICKS)

                        # If the environment can be sustained or some of the item is available
                        if dispenser.stored_items.get(req_item, 0) - (
                                required_item - farm_object.provided_items.get(req_item,
                                                                               0) - farm_object.environment_items.get(
                            req_item, 0)) >= 0:

                            if dispenser.stored_items.get(req_item, None) is not None:
                                dispenser.stored_items[req_item] -= (
                                        required_item - farm_object.provided_items.get(req_item,
                                                                                       0) - farm_object.environment_items.get(
                                    req_item, 0))

                                if farm_object.provided_items.get(req_item, None) is not None:
                                    farm_object.provided_items[req_item] -= (
                                            required_item - farm_object.environment_items.get(
                                        req_item, 0))

                            # TODO: Further testing is needed to confirm that the "environment sustained" code works

                            # Check how many resources is needed from the storage and weather the environment is already sustained/self-sustaining
                            if farm_object.environment_items.get(req_item):
                                farm_object.environment_items[req_item] += (
                                        required_item - farm_object.environment_items.get(req_item, 0))

                            else:
                                farm_object.environment_items[req_item] = (
                                        required_item - farm_object.environment_items.get(req_item, 0))

                            dispenser.stored_items[req_item] = round(dispenser.stored_items[req_item], 7)

                        # If the environment can't be sustained it will enter the items from the provided items
                        elif farm_object.provided_items.get(req_item, 0) > 0:
                            if farm_object.environment_items.get(req_item):
                                farm_object.environment_items[req_item] += farm_object.provided_items[req_item]
                                farm_object.provided_items[req_item] = 0
                            else:
                                farm_object.environment_items[req_item] = farm_object.provided_items[req_item]
                                farm_object.provided_items[req_item] = 0

                    # Stabilise the environment and store any additional unused items
                    for air_item in farm_object.provided_items:
                        if dispenser.stored_items.get(air_item):
                            dispenser.stored_items[air_item] += farm_object.provided_items[air_item]
                            dispenser.stored_items[air_item] = round(dispenser.stored_items[air_item], 7)
                        else:
                            dispenser.stored_items[air_item] = farm_object.provided_items[air_item]

                    # Reset the items provided by the plants
                    farm_object.provided_items = {}

                    # Evaluate the plants
                    for plant_ in farm_object.plants:
                        plant_.evaluate_input(farm_object)
        for farm_ in [self.farm_1, self.farm_2, self.farm_3, self.farm_4]:
            farm_.update(player, pressed_keys, j_ready, dispenser)

        # TODO: Fix this

        self.progress %= FARM_UPDATE_TICKS


# Player class
class Player:
    def __init__(self):
        self.assets = PlayerAssets
        self.movement_ms = 0

        self.direction = "right"
        self.rect = self.assets.player_right.get_rect()
        self.rect.x = 732
        self.rect.y = 496
        self.electricity = 25  # Max energy is 25
        self.electricity_rect = self.assets.energy_bar.get_rect()  # Max energy is 25
        self.electricity_rect.x = 12
        self.electricity_rect.y = 748

        self.dispenser_selected = False
        self.select_ready = True
        self.w_ready = True
        self.s_ready = True
        self.a_ready = True
        self.d_ready = True

        self.electricity_bar = pygame.rect.Rect(16, 752, 0, 40)

        self.items = []

    def blit(self):
        centered_display.blit({"right": self.assets.player_right, "left": self.assets.player_left}[self.direction],
                              self.rect)

        display.blit(self.assets.energy_bar, self.electricity_rect)
        pygame.draw.rect(display, "#FFFFFF", self.electricity_bar)

        if self.items:
            item_rect = self.items[0].image.get_rect()

            item_image = self.items[0].image.copy()

            for x in range(item_image.get_size()[0]):
                for y in range(item_image.get_size()[1]):
                    if self.items[0].image.get_at((x, y))[0]:
                        prev_color = item_image.get_at((x, y))
                        if prev_color[0] - 30 > 0 and prev_color[1] - 30 > 0 and prev_color[2] - 30 > 0:
                            item_image.set_at((x, y), (prev_color[0] - 30, prev_color[1] - 30, prev_color[2] - 30))
                        else:
                            pass

            # item_image.fill("#000000")
            # item_image.set_colorkey("#000000")

            item_rect.center = self.rect.center
            item_rect.bottom = self.rect.top
            item_rect.right = self.rect.right - 8

            if len(self.items) >= 2 and self.rect.left + 8 + self.items[1].image.get_width() > item_rect.left:
                centered_display.blit(item_image, item_rect)
            else:
                centered_display.blit(self.items[0].image, item_rect)

            if len(self.items) >= 2:
                item_rect = self.items[1].image.get_rect()
                item_rect.center = self.rect.center
                item_rect.bottom = self.rect.top
                item_rect.left = self.rect.left + 8

                centered_display.blit(self.items[1].image, item_rect)

    def update(self, keyboard):
        if clock.get_fps() < 55:
            self.movement_ms += clock.get_time()

        if self.movement_ms // (1000 / 240) >= 1 or clock.get_fps() >= 55:
            if not self.dispenser_selected:
                # Movement
                if keyboard[pygame.K_a] and not keyboard[pygame.K_d]:
                    self.direction = "left"
                    if clock.get_fps() < 55:
                        self.rect.x -= (round(240 * (self.movement_ms / 1000) / 4) * 4) // 4 * 4
                    else:
                        self.rect.x -= 4

                if keyboard[pygame.K_d] and not keyboard[pygame.K_a]:
                    self.direction = "right"
                    if clock.get_fps() < 55:
                        self.rect.x += (round(240 * (self.movement_ms / 1000) / 4) * 4) // 4 * 4
                    else:
                        self.rect.x += 4

                if self.rect.x > 1316:
                    self.rect.x = 1316

                if self.rect.x < 20:
                    self.rect.x = 20

            self.movement_ms %= (1000 / 240)

        # Use or drop item
        if not self.dispenser_selected:
            if pressed_keys[pygame.K_l] and self.items and l_ready:
                if player.rect.x >= 1000 and self.items[-1].storable:
                    dispenser.que_item(self.items[-1])
                    self.items = self.items[:-1]

                else:
                    self.items[-1].rect.center = player.rect.center
                    items.append(self.items[-1])
                    self.items = self.items[:-1]

            if pressed_keys[pygame.K_k] and self.items and k_ready:
                for item_ in self.items[::-1]:
                    item_used = item_.use(self)

                    if item_used:
                        self.items.remove(item_)
                        break

                    del item_used

                del item_

        # Electricity
        self.electricity -= clock.get_time() / 24000

        if dev_tools:
            if keyboard[pygame.K_MINUS]:
                self.electricity -= 0.25

            if keyboard[pygame.K_EQUALS]:
                self.electricity += 0.25

        if self.electricity > 25:
            self.electricity = 25

        if self.electricity < 0:
            self.electricity = 0

        if self.electricity == 25:
            self.electricity_bar.width = 400
        elif self.electricity == 0:
            self.electricity_bar.width = 0
        else:
            self.electricity_bar.width = int(((((self.electricity / 25) * 400) // 4) * 4) + 4)

        self.electricity_rect.y = screen.get_height() - 64
        self.electricity_bar.y = screen.get_height() - 60

        # Ui
        if pressed_keys[pygame.K_e] and self.select_ready and self.dispenser_selected:
            self.dispenser_selected = False
        elif player.rect.x >= 1000 and pressed_keys[pygame.K_e] and self.select_ready:
            self.dispenser_selected = True

        self.ui_interaction()

        # Select ready
        if pressed_keys[pygame.K_e]:
            self.select_ready = False
        else:
            self.select_ready = True

        # Up ready
        if pressed_keys[pygame.K_w]:
            self.w_ready = False
        else:
            self.w_ready = True

        # Down ready
        if pressed_keys[pygame.K_s]:
            self.s_ready = False
        else:
            self.s_ready = True

        # Left ready
        if pressed_keys[pygame.K_a]:
            self.a_ready = False
        else:
            self.a_ready = True

        # Right ready
        if pressed_keys[pygame.K_d]:
            self.d_ready = False
        else:
            self.d_ready = True

    def pickup(self):
        if len(self.items) != 2:
            self.items.append(pickup_items[min(pickup_items.keys())])
            items_register.items.remove(pickup_items[min(pickup_items.keys())])

    def ui_interaction(self):
        if self.dispenser_selected:
            if dispenser.entry == "unselected":
                if pressed_keys[pygame.K_s] and self.s_ready:
                    dispenser.lit_option = entries[
                        (entries.index(dispenser.lit_option) + 1) % len(entries)]
                    SFXDispenser.switch.play()

                if pressed_keys[pygame.K_w] and self.w_ready:
                    dispenser.lit_option = entries[
                        ((entries.index(dispenser.lit_option) - 1) + len(entries)) % len(entries)]
                    SFXDispenser.switch.play()

                if pressed_keys[pygame.K_j] and j_ready:
                    dispenser.switch_entry(dispenser.lit_option)
                    SFXDispenser.select.play()

            if pressed_keys[pygame.K_l] and l_ready and len(dispenser.history) >= 2:
                dispenser.entry = dispenser.history[-2]
                dispenser.history = dispenser.history[:-1]


holograms = Holograms()
dispenser = Dispenser()
generator = Generator()
farms = Farms()
player = Player()

# def no_function():
#     pass


# def leaf_temp(item_: Item):
#     item_.x_shift = 0
#     if not item_.floored:
#         item_.rect.x = item_.orig_x
#
#     if item_.has_gravity and item_.rect.y < 552:
#         item_.gravity -= (clock.get_time() / 1000) * (9.7 * 45)
#
#     if item_.has_gravity and item_.gravity > 20:
#         item_.gravity = 20
#
#     if not item_.floored:
#         item_.x_shift = math.sin((pygame.time.get_ticks() / 200) + item_.sin_shift) * 20
#         item_.rect.x += item_.x_shift
#         item_.rect.x = (item_.rect.x // 4) * 4
#         # item.rect.y = (item.rect.y // 4) * 4


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.WINDOWRESIZED:
            display = pygame.surface.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            centered_display = pygame.surface.Surface((screen.get_width() - (screen.get_width() - 1400),
                                                       screen.get_height() - (screen.get_height() - 800)),
                                                      pygame.SRCALPHA)
            overlay = pygame.surface.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)

            items_register.register(pygame, clock, display=display, centered_display=centered_display, overlay=overlay)

            plants_register.register(pygame, clock, screen=screen, display=display, centered_display=centered_display,
                                     overlay=overlay)

            farm_creator.register(pygame, clock, screen=screen, display=display, centered_display=centered_display,
                                  overlay=overlay)

            environment_effects.register(pygame, clock, screen=screen, display=display,
                                         centered_display=centered_display,
                                         overlay=overlay)

    screen.fill("#303033")
    display.fill("#30303300")
    centered_display.fill("#30303300")
    overlay.fill("#30303300")

    mouse_pos = pygame.mouse.get_pos()
    mouse_keys = pygame.mouse.get_pressed()

    pressed_keys = pygame.key.get_pressed()

    items_register.pickup_items = {}
    items = items_register.items
    pickup_items = items_register.pickup_items

    if mode == "menu":
        if not pygame.mixer.get_busy():
            ost_authorised.play(1)

        # Shooting star
        if random.randint(0, 20) == 20:
            star_x = random.randint(300, 3000)
            star_y = random.randint(-600, -300)

            star_x = (star_x // 4) * 4
            star_y = (star_y // 4) * 4

            stars.append([star_x, star_y, random.choice([0, 1, 2])])

        for star_idx in range(len(stars)):
            stars[star_idx][0] -= 4
            stars[star_idx][1] += 4

            if stars[star_idx][0] <= -300:
                stars[star_idx] = []

            elif stars[star_idx][1] >= 3000:
                stars[star_idx] = []

        while [] in stars:
            stars.remove([])

        # Layered shooting stars
        for star_idx in range(len(stars)):
            if stars[star_idx][2] == 2:
                display.blit(shooting_star_3, (stars[star_idx][0], stars[star_idx][1]))

        for star_idx in range(len(stars)):
            if stars[star_idx][2] == 1:
                display.blit(shooting_star_2, (stars[star_idx][0], stars[star_idx][1]))

        for star_idx in range(len(stars)):
            if stars[star_idx][2] == 0:
                display.blit(shooting_star_1, (stars[star_idx][0], stars[star_idx][1]))

        # Title
        display.blit(title, (40, 40))

        # Play button
        play_button_rect.x = 40
        play_button_rect.y = 80

        if play_button_rect.collidepoint(mouse_pos):
            display.blit(play_button_lit, (play_button_rect.x, play_button_rect.y))

            if mouse_keys[0] and mouse_lifted:
                pygame.mixer.stop()
                mode = "play"
        else:
            display.blit(play_button_dark, (play_button_rect.x, play_button_rect.y))

        # Glitch effects
        glitch_toggle_rect.x = 40
        glitch_toggle_rect.y = 140

        if glitch_toggle_rect.collidepoint(mouse_pos) and mouse_keys[0] and mouse_lifted:
            glitch_effects = not glitch_effects

        if glitch_effects:
            display.blit(glitch_effect_on, glitch_toggle_rect)
        else:
            display.blit(glitch_effect_off, glitch_toggle_rect)

    if mode == "setup":
        pass

    elif mode == "play":
        # TEST
        if dev_tools and pressed_keys[pygame.K_i]:
            test_item = items_register.AirItem()
            items.append(test_item)

        # Update
        dispenser.update()
        generator.update()
        farms.update()
        player.update(pressed_keys)

        # Items
        for item in items:
            item.update(player, pressed_keys, j_ready)

            if pressed_keys[pygame.K_o] and dev_tools:
                if item.dispensable:
                    item.rect.y = 0
                    item.gravity = 0
                    item.floored = False

            del item

        # Dev tools
        if dev_tools and pressed_keys[pygame.K_i]:
            # test_item =  TestItem(random.randint(40, 1000), 0, True, random.randint(-10, 10))
            test_item = items_register.TestItem(random.randint(40, 1000), 0, True)
            items.append(test_item)

            test_item = items_register.CompressedEnergyLeavesItem(random.randint(40, 1000), 0, True)
            items.append(test_item)

            test_item = items_register.EnergyLeafItem(random.randint(40, 1000), 0, True)
            items.append(test_item)

            del test_item

        if dev_tools and pressed_keys[pygame.K_p]:
            items_register.items = []
            items = []

        if dev_tools and pressed_keys[pygame.K_r]:
            dispenser.screen_mode = 3

        if dev_tools and pressed_keys[pygame.K_b]:
            pass
            # new_plant = plants_register.Plant(random.randint(228, 1028) // 4 * 4, "lush")
            # plants.append(new_plant)

        if dev_tools and pressed_keys[pygame.K_m]:
            pass
            # plants = []

        # Blit
        dispenser.blit()
        generator.blit()

        # NOTICE: repurpose this code and make each farm run this for its plants [is this done yet?]
        for farm in [farms.farm_1, farms.farm_2, farms.farm_3, farms.farm_4]:
            for plant in farm.plants:
                plant.blit()

        farms.blit()

        player.blit()

        for item in items:
            item.blit()

        # Pickup item
        if pickup_items:
            player.pickup()

        items = items_register.items
        pickup_items = items_register.pickup_items

        centered_display.blit(RoomAssets.room_outline, (20, 200))

        if mouse_keys[0]:
            print((mouse_pos[0] // 4) * 4, (mouse_pos[1] // 4) * 4)

        if not glitch_effects:
            if player.electricity < 5:
                hex_opacity = hex(int(200 - (player.electricity * 51)))[2:]

                if len(hex_opacity) == 1:
                    hex_opacity = "0" + hex_opacity

                elif (200 - (player.electricity * 51)) < 0:
                    hex_opacity = "00"

                elif len(hex_opacity) == 3:
                    hex_opacity = "FF"

                overlay.fill("#000000" + hex_opacity)

        elif glitch_effects and not enhanced_glitch_effects:
            pass

        elif glitch_effects and enhanced_glitch_effects:
            if player.electricity < 3:
                if random.randint(0, int(player.electricity) ** 2) == 0:
                    for _ in range(random.randint(0, 3 - int(player.electricity))):
                        overlay.blit(energy_depleting_glitching,
                                     (random.randint(0, screen.get_width()), random.randint(0, screen.get_height())))

                energy_depleting_glitching.set_alpha(150 - int(player.electricity) * 50)

        if dev_tools:
            display.blit(spacebar_command, (4, 4))
            display.blit(o_command, (4, 36))
            display.blit(i_command, (4, 70))
            display.blit(l_command, (4, 104))

    # Mouse lifted
    if mouse_keys[0] or mouse_keys[2]:
        mouse_lifted = False
    else:
        mouse_lifted = True

    # Pickup ready
    if pressed_keys[pygame.K_j]:
        j_ready = False
    else:
        j_ready = True

    # Item use ready
    if pressed_keys[pygame.K_k]:
        k_ready = False
    else:
        k_ready = True

    # Drop ready
    if pressed_keys[pygame.K_l]:
        l_ready = False
    else:
        l_ready = True

    if pressed_keys[pygame.K_f] or True:
        # TODO: finish
        # Finish what
        fps = str(int(clock.get_fps()))
        for i in range(len(fps)):
            display.blit(number_ref[fps[i]], (4 + 16 * i, screen.get_height() - 92))

    # Pygame update

    if pressed_keys[pygame.K_f]:
        item_list = dispenser.stored_items
        # print(item_list)
        # print(farms.farm_1)
        # print(item_list)
        # print()
        print(farms.farm_1.environment_items)
        del item_list

    screen.blit(centered_display, ((screen.get_width() - 1400) / 2, (screen.get_height() - 800) / 2))
    screen.blit(display, (0, 0))
    screen.blit(overlay, (0, 0))

    if mouse_keys[0]:
        print(screen.get_at(mouse_pos))

    item_list_ = list(dispenser.stored_items)
    item_list_.sort()
    print(dispenser.stored_items[item_list_[dispenser.current_item]], "item")
    print("------------------------------------")

    # print(clock.get_fps())
    # print(dispenser.fabricating_items)

    clock.tick(60)

    pygame.display.update()
