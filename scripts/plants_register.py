# TODO: Rename ???_progress to ???_timer
import copy
import random

from scripts.assets import FarmAssets
from scripts.farms import Farm

FARM_UPDATE_TICKS = 1000  # PLACEHOLDER TO BE OVERRIDE BY MAIN


def register(pygame_module, clock_, **surfaces):
    global pygame
    global clock
    global screens

    pygame = pygame_module
    clock = clock_
    screens = surfaces


# A reference containing all the plants
plant_ref = {}


def register_plant(plant):
    """Register a plant"""
    plant_ref[plant.name] = plant


def init_plant_rect(rect, x):
    """Initiate the rect of the plant"""
    rect.left = ((x - 224) // 204 * 204) + 228
    rect.bottom = 464


class Plant:
    """The parent class for all flora."""
    name = "plant"

    def __init__(self, x: int, environment: str):
        # Required variables
        self.image = FarmAssets.blank_canvas.copy()
        self.rect = self.image.get_rect()

        # Rect stuff
        self.rect.x = x
        init_plant_rect(self.rect, x)

        # TODO: Remove this in the next commit
        self.rect.bottom = 464

    def blit(self):
        """Override this when needed, however mostly just leave it alone."""
        screens["centered_display"].blit(self.image, self.rect)

    def update(self, player, pressed_keys, pickup_ready, farm: Farm, dispenser):
        """ALWAYS OVERRIDE THIS TO ADD YOUR OWN MODIFICATIONS"""
        self.grow()
        self.inject_update(player, pressed_keys, pickup_ready, farm, dispenser)
        pass

    def inject_update(self, player, pressed_keys, pickup_ready, farm: Farm, dispenser):
        """Only modify when inheriting from a child of this class, and run this in update for the class to be easily inheritable"""
        pass

    @staticmethod
    def evaluate_output(farm: Farm):
        """What materials does the plant need to consume in order to be maintained"""
        pass

    def evaluate_input(self, farm: Farm):
        """What materials does the plant produce"""
        pass

    def grow(self):
        """Override this to add your own growth functionality, remember to call in update"""
        pass


def pale_moss_synergy(func):
    """A decorator that adds the feature of a plants cooldowns to be reduced by pale moss"""

    def wrapper(self, player, pressed_keys, pickup_ready, farm: Farm, dispenser):
        time_reduction_percent = 0

        for entry in farm.plants:
            if type(entry) == PaleMoss:
                time_reduction_percent += entry.flowers

        for i in range(len(self.cooldowns)):
            self.cooldowns[i] = self.cooldown_constants[i] - self.cooldown_constants[i] * (time_reduction_percent / 100)

        func(self, player, pressed_keys, pickup_ready, farm, dispenser)
        # self.grow_cooldown = self.GROW_COOLDOWN_CONST - self.GROW_COOLDOWN_CONST * (time_reduction_percent / 100)
        # self.bulb_move_cooldown = self.BULB_MOVE_CONST - self.BULB_MOVE_CONST * (time_reduction_percent / 100)

    return wrapper


class PaleBushPlant(Plant):
    # The seeds are beans that hang from the bush but im too lazy to make them show up
    name = "pale-bush"

    def __init__(self, x: int, environment: str):
        super().__init__(x, environment)

        # Required variables
        self.image = FarmAssets.blank_canvas.copy()
        self.rect = self.image.get_rect()

        self.x = x
        init_plant_rect(self.rect, x)

        # Growth cooldown
        self.cooldown_progress = 0
        self.grow_cooldown = 300  # 0.3 seconds
        self.GROW_COOLDOWN_CONST = 300  # 0.3 seconds

        # Pale leaf creation cooldown
        self.generate_leaf_progress = 0
        self.generate_cooldown = 1000
        self.GENERATE_COOLDOWN_CONST = 1000

        # Seed creation
        self.seed_progress = 0
        self.SEED_COOLDOWN = 1200000

        # All cooldowns that can be reduced by pale moss
        self.cooldowns = [self.grow_cooldown, self.generate_cooldown]
        self.cooldown_constants = [self.GROW_COOLDOWN_CONST, self.GENERATE_COOLDOWN_CONST]

        # All the leaves on the bush
        self.leaves = []

        # The width and height of the bush, I don't know if height even does anything, but I don't want to check
        self.width = 4
        self.height = 4

        # If the bush can still grow
        self.growing = True
        self.overall_time = 0  # DELETE LATER

        # Does nothing [delete next commit]
        self.time_reduced = False

    def blit(self):
        # TODO: Remove this next commit since it doesn't override the base function
        screens["centered_display"].blit(self.image, self.rect)

    @pale_moss_synergy
    def update(self, player, pressed_keys, pickup_ready, farm: Farm, dispenser):
        print(self.seed_progress, "bush")

        # Grow the bush
        self.generate_cooldown = self.cooldowns[1]
        self.grow()

        # Progress the timer
        self.generate_leaf_progress += clock.get_time()
        self.seed_progress += clock.get_time()

        # Add the energy leaf entry if it hasn't been discovered yet
        if not dispenser.stored_items.get("energy-leaf"):
            item_list = list(dispenser.stored_items.keys())
            item_list.sort()

            current_item = item_list[dispenser.current_item]

            dispenser.stored_items["energy-leaf"] = 0

            item_list = list(dispenser.stored_items.keys())
            item_list.sort()

            dispenser.current_item = item_list.index(current_item)

        # Cap the cooldown to prevent pale moss from throwing it into the negetives
        if self.generate_cooldown <= 0:
            self.generate_cooldown = 1

        # Grow pale leaves
        for _ in range(int(self.generate_leaf_progress // self.generate_cooldown)):
            dispenser.stored_items["energy-leaf"] += 1

        # Grow pale bush seeds
        for _ in range(int(self.seed_progress // self.SEED_COOLDOWN)):
            if not dispenser.stored_items.get("pale-bush-seed"):
                # Add the pale bush seed entry if it doesn't already exist
                item_list = list(dispenser.stored_items.keys())
                item_list.sort()

                current_item = item_list[dispenser.current_item]

                dispenser.stored_items["pale-bush-seed"] = 1

                item_list = list(dispenser.stored_items.keys())
                item_list.sort()

                dispenser.current_item = item_list.index(current_item)
            else:
                dispenser.stored_items["pale-bush-seed"] += 1

        # 160.19 is the width

        # 0.005 po/second
        # 1 po from one leaf

        # self.generate_cooldown = 6000000 / self.width
        # Reduce how long it take to grow a leaf based on the size of the bush
        self.GENERATE_COOLDOWN_CONST = 6000000 / self.width

        # All cooldowns that can be reduced by pale moss
        self.cooldowns = [self.grow_cooldown, self.generate_cooldown]
        self.cooldown_constants = [self.GROW_COOLDOWN_CONST, self.GENERATE_COOLDOWN_CONST]

        # Reset the timers
        self.generate_leaf_progress %= self.generate_cooldown
        self.seed_progress %= self.SEED_COOLDOWN

    @staticmethod
    def evaluate_output(farm: Farm):
        # Generates pale argon (0.01 / s)
        if farm.provided_items.get("pale-argon", None) is not None:
            farm.provided_items["pale-argon"] += 0.01 / (1000 / FARM_UPDATE_TICKS)
        else:
            farm.provided_items["pale-argon"] = 0.01 / (1000 / FARM_UPDATE_TICKS)

    def evaluate_input(self, farm):
        # Consumes pale air (0.01 / s)
        if farm.environment_items.get("pale-air", None) is not None and farm.environment_items.get("pale-air") > 0:

            if farm.provided_items.get("pale-air", 0) - 0.01 / (1000 / FARM_UPDATE_TICKS) >= 0:
                farm.provided_items["pale-air"] -= 0.01 / (1000 / FARM_UPDATE_TICKS)

            else:
                if farm.provided_items.get("pale-air", None) is not None:
                    farm.environment_items["pale-air"] -= (
                            0.01 / (1000 / FARM_UPDATE_TICKS) - farm.provided_items["pale-air"])
                    farm.provided_items["pale-air"] = 0 / (1000 / FARM_UPDATE_TICKS)

                else:
                    farm.environment_items["pale-air"] -= 0.01 / (1000 / FARM_UPDATE_TICKS)
        else:
            farm.plants.remove(self)

    def grow(self):
        # print(self.generate_cooldown, "," ,self.GENERATE_COOLDOWN_CONST)

        new_area = random.choice([FarmAssets.leaf_brush_1, FarmAssets.leaf_brush_2, FarmAssets.leaf_brush_3,
                                  FarmAssets.leaf_brush_4, FarmAssets.leaf_brush_5, FarmAssets.leaf_brush_6])

        # Grow leaves
        if self.leaves:
            loc_x = random.randint(-int(self.width / 2), int(self.width / 2))
            loc_y = (((self.width / 2) ** 2) - (loc_x ** 2)) ** (1 / 2)

            if loc_x >= 40:
                loc_x = random.randint(24, 56)

            if loc_x <= -40:
                loc_x = random.randint(-56, -24)

            loc = [(self.x - self.rect.x + loc_x) // 4 * 4, (212 - loc_y) // 4 * 4]

        else:
            # Force the first leaf to be centered
            loc = [self.x - self.rect.x, 212]

        color = "#FFFFFF"

        # if random.random() > 0.6 or not self.leaves:
        #     color = random.choice(["#979797", "#aaaaaa", "#c0c0c0", "#cfcfcf"])
        # elif self.leaves:
        #     pass
        # hex_value = hex(int(str(leaf_choice[2][1:3]), 16) + random.randint(0, 16))[2:]
        # if len(hex_value) >= 3:
        #     hex_value = "FF"
        # elif len(hex_value) == 1:
        #     hex_value = "0" + hex_value
        # elif len(hex_value) <= 0:
        #     hex_value = "00"
        #
        # color = "#" + hex_value * 3

        color: str

        # I don't think this code does anything
        if self.leaves:
            for x in range(new_area.get_width()):
                for y in range(new_area.get_height()):
                    if new_area.get_at((x, y)).a == 255:
                        new_area.set_at((x, y), color)

        # if self.growing:
        #     self.overall_time += clock.get_time()

        # Grow leaves
        if self.cooldown_progress >= self.grow_cooldown and self.growing:
            for _ in range(self.cooldown_progress // self.grow_cooldown):
                if random.random() < 0.0289:
                    # Batch of layered leaves
                    color = "#979797"

                    for i in range(4):
                        self.new_leaf(color, loc)

                        hex_value = hex(int(str(color[1:3]), 16) + 16)[2:]
                        if len(hex_value) >= 3:
                            hex_value = "FF"
                        elif len(hex_value) == 1:
                            hex_value = "0" + hex_value
                        elif len(hex_value) <= 0:
                            hex_value = "00"

                        color = "#" + hex_value * 3

                        loc[0] += 4
                        loc[1] += 4

                    loc[0] -= 16
                    loc[1] -= 16
                else:
                    # Regular leaf
                    for x in range(new_area.get_width()):
                        for y in range(new_area.get_height()):
                            if new_area.get_at((x, y)).a == 255:
                                new_area.set_at((x, y), "#979797")

                    pseudo_image = FarmAssets.blank_canvas.copy()
                    pseudo_image.blit(new_area, loc)
                    pseudo_image.blit(self.image, (0, 0))
                    self.image = pseudo_image
                    del pseudo_image

                # Increase the size
                if self.width < 160:
                    self.width += 0.2
                    self.height += 0.2
                else:
                    self.growing = False

            # Reset the timer
            self.cooldown_progress %= self.grow_cooldown
        else:
            # Progress the timer
            self.cooldown_progress += clock.get_time()

        # Append the leaf
        self.leaves.append(loc + [color])

    def new_leaf(self, color, loc):
        # if abs(loc[0]) >= 40:
        #     loc[0] = 40 * (loc[0] / abs(loc[0]))

        # Copy the variable so it isn't linked
        loc_cop = copy.deepcopy(loc)

        # Leaf brushes
        new_area = random.choice([FarmAssets.leaf_brush_1, FarmAssets.leaf_brush_2, FarmAssets.leaf_brush_3,
                                  FarmAssets.leaf_brush_4, FarmAssets.leaf_brush_5, FarmAssets.leaf_brush_6])

        # Change the leaf based on the colour
        for x in range(new_area.get_width()):
            for y in range(new_area.get_height()):
                if new_area.get_at((x, y)).a == 255:
                    new_area.set_at((x, y), color)

        # Blit the leaf onto the canvas directly
        pseudo_image = FarmAssets.blank_canvas.copy()
        pseudo_image.blit(new_area, loc_cop)
        self.image.blit(pseudo_image, (0, 0))
        del pseudo_image


register_plant(PaleBushPlant)


class LightBulbFern(Plant):
    # The seed come from the stem in the middle the 'fruit' is used for a different purpose (to be decided)
    name = "light-bulb-fern"

    def __init__(self, x: int, environment: str):
        super().__init__(x, environment)

        # Required variables
        self.image = FarmAssets.blank_canvas.copy()
        self.rect = self.image.get_rect()

        # Bulbs and branches
        self.bulb_positions = []
        self.branch_positions = []

        # Rect
        init_plant_rect(self.rect, x)
        self.x = x

        # Where the stem should be at
        self.stem_y = 212
        self.stem_x = 0

        # Growth cooldown
        self.grow_progress = 0
        self.grow_cooldown = 10000  # 0.3 seconds
        self.GROW_COOLDOWN_CONST = 10000

        # Bulb decent cooldown
        self.bulb_move_progress = 0
        self.bulb_move_cooldown = 80000
        self.BULB_MOVE_CONST = 80000

        # Seed creation cooldown
        self.seed_progress = 0  # Unaffected by pale moss
        self.seed_cooldown = 1200000  # Rework the cooldown to be more reasonable

        # All cooldowns that can be reduced by pale moss
        self.cooldowns = [self.grow_cooldown, self.bulb_move_cooldown]
        self.cooldown_constants = [self.GROW_COOLDOWN_CONST, self.BULB_MOVE_CONST]

        # If the plant can still grow in size
        self.growing = True
        self.overall_time = 0  # Measure how long the plant grows for [DELETE LATER]

        # Bulb assets
        self.bulb_stages = {1: FarmAssets.lightbulb_fern_pa_bulb_1, 2: FarmAssets.lightbulb_fern_pa_bulb_2,
                            3: FarmAssets.lightbulb_fern_pa_bulb_3}

        # Reference to the dispenser for items
        self.dispenser_ref = None

        # Does nothing [delete next commit]
        self.time_reduced = False

    @pale_moss_synergy
    def update(self, player, pressed_keys, pickup_ready, farm: Farm, dispenser):
        print(self.seed_progress, "ligh bulb")

        # Link the dispenser with the dispenser reference
        self.dispenser_ref = dispenser

        # Progress the timer
        self.overall_time += clock.get_time()
        self.seed_progress += clock.get_time()
        self.bulb_move_progress += clock.get_time()
        self.grow_progress += clock.get_time()

        # Grow light bulb fern seeds
        for _ in range(self.seed_progress // self.seed_cooldown):
            if not dispenser.stored_items.get("light-bulb-fern-seed"):
                # Add the light bulb fern seed entry if it doesn't exist
                item_list = list(dispenser.stored_items.keys())
                item_list.sort()

                current_item = item_list[dispenser.current_item]

                dispenser.stored_items["light-bulb-fern-seed"] = 1

                item_list = list(dispenser.stored_items.keys())
                item_list.sort()

                dispenser.current_item = item_list.index(current_item)
            else:
                dispenser.stored_items["light-bulb-fern-seed"] += 1

        # Reset the timers
        self.seed_progress %= self.seed_cooldown

        # Grow the plant
        self.grow()

        # Update the stem x
        self.stem_x = self.x - farm.x

        # Blit
        self.blit()

        # self.grow_cooldown = self.cooldowns[0]
        # self.bulb_move_cooldown = self.cooldowns[1]

    def blit(self):
        # Canvases
        bulb_image = self.image.copy()
        branch_image = self.image.copy()
        tip_image = self.image.copy()

        # Blit the bulbs onto a canvas
        for bulb in self.bulb_positions:
            if bulb[2] <= 3:
                bulb_image.blit(self.bulb_stages[bulb[2]], bulb[:2])

        # Blit the branches onto a canvas
        for branch in self.branch_positions:
            branch_image.blit(FarmAssets.lightbulb_fern_branch, branch)

        # Blit the tip of the fern
        tip_image.blit(FarmAssets.lightbulb_fern_tip, (self.x - self.rect.x, self.stem_y + 244 - self.rect.y))

        # Display the canvases
        screens["centered_display"].blit(self.image, self.rect)
        screens["centered_display"].blit(branch_image, self.rect)
        screens["centered_display"].blit(bulb_image, self.rect)
        screens["centered_display"].blit(tip_image, self.rect)

    @staticmethod
    def evaluate_output(farm: Farm):
        # Generates pale air/oxygen (0.01 / s)
        if farm.provided_items.get("pale-air", None) is not None:
            farm.provided_items["pale-air"] += 0.01 / (1000 / FARM_UPDATE_TICKS)
        else:
            farm.provided_items["pale-air"] = 0.01 / (1000 / FARM_UPDATE_TICKS)

    def evaluate_input(self, farm):
        # Consumes pale argon (0.01 / s)
        if farm.environment_items.get("pale-argon", None) is not None and farm.environment_items.get("pale-argon") > 0:

            if farm.provided_items.get("pale-argon", 0) - 0.01 / (1000 / FARM_UPDATE_TICKS) >= 0:
                farm.provided_items["pale-argon"] -= 0.01 / (1000 / FARM_UPDATE_TICKS)

            else:
                if farm.provided_items.get("pale-argon", None) is not None:
                    farm.environment_items["pale-argon"] -= (
                            0.01 / (1000 / FARM_UPDATE_TICKS) - farm.provided_items["pale-argon"])
                    farm.provided_items["pale-argon"] = 0 / (1000 / FARM_UPDATE_TICKS)

                else:
                    farm.environment_items["pale-argon"] -= 0.01 / (1000 / FARM_UPDATE_TICKS)
        else:
            farm.plants.remove(self)

    def grow(self):
        # print(self.overall_time, self.growing)

        if self.growing:
            if self.grow_progress >= self.grow_cooldown:
                # Grow higher
                for _ in range(self.grow_progress // self.grow_cooldown):
                    self.stem_y -= 4
                    self.image.blit(FarmAssets.lightbulb_fern_stem, (self.stem_x, self.stem_y))

                    if self.stem_y + 252 <= 464 - 4 * 26:
                        # Stop growing if the fern is at maximum height
                        self.growing = False

                # if self.stem_y + 252 == 464 - 4 * 6:
                #     self.spawn_bulb()

                # Grow the stem and bulbs if it's above a certain height
                if (208 - self.stem_y - 4 * 6) % (7 * 4) == 0:
                    self.enrich_bulbs()
                    self.spawn_bulb()

                # Reset the timer
                self.grow_progress %= self.grow_cooldown

        else:
            if self.bulb_move_progress >= self.bulb_move_cooldown:
                for _ in range(self.bulb_move_progress // self.bulb_move_cooldown):
                    # Move the bulbs down to be harvested
                    self.progress_bulbs()

                # if self.stem_y + 252 == 464 - 4 * 6:
                #     self.spawn_bulb()

                # if (208 - self.stem_y - 4 * 6) % (7 * 4) == 0:
                #     self.spawn_bulb()

                # Reset the time
                self.bulb_move_progress %= self.bulb_move_cooldown

    def spawn_bulb(self):
        # UNUSED CODE for making the bulb positions random
        outcomes = [0]

        # Grow a bulb
        self.bulb_positions.append(
            [self.stem_x - 20 + random.choice(outcomes), self.stem_y - 4 + random.choice(outcomes), 1])
        self.bulb_positions.append(
            [self.stem_x + 12 + random.choice(outcomes), self.stem_y - 4 + random.choice(outcomes), 1])

        # Grow the branches for the bulb
        self.branch_positions.append([self.stem_x - 16, self.stem_y])
        self.branch_positions.append([self.stem_x - 12, self.stem_y])
        self.branch_positions.append([self.stem_x - 8, self.stem_y])
        self.branch_positions.append([self.stem_x - 4, self.stem_y])

        self.branch_positions.append([self.stem_x + 8, self.stem_y])
        self.branch_positions.append([self.stem_x + 12, self.stem_y])
        self.branch_positions.append([self.stem_x + 16, self.stem_y])
        self.branch_positions.append([self.stem_x + 20, self.stem_y])
        # self.branch_positions.append([self.stem_x + 16, self.stem_y])

    def enrich_bulbs(self):
        for bulb in self.bulb_positions:
            # Increase the bulbs size
            bulb[2] += 1

            # Push the bulbs outwards
            if bulb[0] < self.stem_x:
                bulb[0] -= 8

            elif bulb[0] > self.stem_x:
                bulb[0] += 4

            # Add branches if the bulb size is max size
            if bulb[2] == 3:
                if bulb[0] < self.stem_x:
                    self.branch_positions.append([self.stem_x - 16, bulb[1] + 8])
                    self.branch_positions.append([self.stem_x - 12, bulb[1] + 8])
                    self.branch_positions.append([self.stem_x - 8, bulb[1] + 8])
                    self.branch_positions.append([self.stem_x - 4, bulb[1] + 8])

                else:
                    self.branch_positions.append([self.stem_x + 8, bulb[1] + 8])
                    self.branch_positions.append([self.stem_x + 12, bulb[1] + 8])
                    self.branch_positions.append([self.stem_x + 16, bulb[1] + 8])
                    self.branch_positions.append([self.stem_x + 20, bulb[1] + 8])

    def progress_bulbs(self):
        # Push the bulbs down
        for bulb_idx in range(len(self.bulb_positions)):
            self.bulb_positions[bulb_idx][1] += 4
            if self.bulb_positions[bulb_idx][1] == 184:
                # Harvest bulbs at the bottom
                self.bulb_positions[bulb_idx] = ""

        grow_bulbs = False
        if "" in self.bulb_positions:
            grow_bulbs = True

        # Remove the harvested bulbs (this method is used to prevent the list from desynchronizing during the loop)
        while "" in self.bulb_positions:
            self.bulb_positions.remove("")

            # Add the light bulb fern orb entry if it hasn't been discovered yet
            if self.dispenser_ref.stored_items.get("lightbulb-fern-orb"):
                self.dispenser_ref.stored_items["lightbulb-fern-orb"] += 1
            else:
                self.dispenser_ref.stored_items["lightbulb-fern-orb"] = 1

        # Loop through the branches
        for branch_idx in range(len(self.branch_positions)):
            # Move the branches down
            self.branch_positions[branch_idx][1] += 4

            # Remove branches at the bottom
            if self.branch_positions[branch_idx][1] > 200 - (
                    abs((self.stem_x + 2) - self.branch_positions[branch_idx][0]) - 2):
                self.branch_positions[branch_idx] = ""

        # Remove branches (this method is used to prevent the list from desynchronizing during the loop)
        while "" in self.branch_positions:
            self.branch_positions.remove("")

        if grow_bulbs:
            # When a bulb gets remove enrich and spawn new bulbs
            self.enrich_bulbs()

            for _ in range(6 - len(self.bulb_positions) // 2):
                self.spawn_bulb()


register_plant(LightBulbFern)


class PaleMoss(Plant):
    # The 'seed' is just a swathe that was created by taking pieces of the moss from different places
    name = "pale-moss"

    def __init__(self, x, environment: str):
        super().__init__(x, environment)

        # Required variables
        self.image = FarmAssets.blank_canvas.copy()
        self.rect = self.image.get_rect()

        # Canvas
        self.flower_image = FarmAssets.blank_canvas.copy()

        # Rect stuff
        self.x = x
        init_plant_rect(self.rect, x)

        # Shift variables
        self.left_shift = 0
        self.left_growing = True

        self.right_shift = 0
        self.right_growing = True

        self.shift_increment_progress = 0
        self.SHIFT_INCREMENT_COOLDOWN = 5000

        # Grow timer
        self.grow_progress = 0
        self.GROW_COOLDOWN = 1250

        # Flower timer
        self.flower_progress = 0
        self.FLOWER_COOLDOWN = 27500

        # Seed timer
        self.seed_progress = 0
        self.SEED_COOLDOWN = 1200000

        # Flowers count
        self.flowers = 0

        # If the plant can still grow in size
        self.growing = True

    def blit(self):
        # Blit the stuff
        screens["centered_display"].blit(self.image, self.rect)
        screens["centered_display"].blit(self.flower_image, self.rect)

    def update(self, player, pressed_keys, pickup_ready, farm: Farm, dispenser):
        print(self.seed_progress, "pale moss")
        # print(self.rect, farm.x, self.x)

        # pygame.draw.rect(screens["centered_display"], "#FFFFFF", self.rect)

        # Increase the timer
        self.shift_increment_progress += clock.get_time()
        self.grow_progress += clock.get_time()
        self.flower_progress += clock.get_time()
        self.seed_progress += clock.get_time()

        # Grow the plant
        for _ in range(self.grow_progress // self.GROW_COOLDOWN):
            # print(self.flowers, "flowers")
            self.grow()

        # Increase where the moss can go
        for _ in range(self.shift_increment_progress // self.SHIFT_INCREMENT_COOLDOWN):
            if self.x - self.rect.x - self.left_shift < farm.x:
                self.left_shift += 4
            else:
                # Stop the moss from out of the farm
                self.left_growing = False

            if self.x - self.rect.x + self.right_shift < 196:
                self.right_shift += 4
            else:
                # Stop the moss from out of the farm
                self.right_growing = False

        # Grow flowers
        for _ in range(self.flower_progress // self.FLOWER_COOLDOWN):
            side = random.choice(["right", "left"])

            if self.right_growing and side == "right":
                self.flower_image.blit(FarmAssets.moss_flowers,
                                       (self.x - self.rect.x + self.right_shift + random.choice([-4, 0, 4]),
                                        444 - 252 + random.choice([12, 8, 4, 0])))

            if self.left_growing and side == "left":
                self.flower_image.blit(FarmAssets.moss_flowers,
                                       (self.x - self.rect.x - self.left_shift + random.choice([-4, 0, 4]),
                                        444 - 252 + random.choice([12, 8, 4, 0])))

            self.flowers += 1

        # Grow pale moss swathes
        for _ in range(self.seed_progress // self.SEED_COOLDOWN):
            if not dispenser.stored_items.get("pale-moss-swathe"):
                # Add the pale moss swathe entry if it hasn't been discovered yet
                item_list = list(dispenser.stored_items.keys())
                item_list.sort()

                current_item = item_list[dispenser.current_item]

                dispenser.stored_items["pale-moss-swathe"] = 1

                item_list = list(dispenser.stored_items.keys())
                item_list.sort()

                dispenser.current_item = item_list.index(current_item)
            else:
                dispenser.stored_items["pale-moss-swathe"] += 1

        # Reset the timers
        self.shift_increment_progress %= self.SHIFT_INCREMENT_COOLDOWN
        self.grow_progress %= self.GROW_COOLDOWN
        self.flower_progress %= self.FLOWER_COOLDOWN
        self.seed_progress %= self.SEED_COOLDOWN

    def evaluate_output(self, farm: Farm):
        # No output
        pass

    def evaluate_input(self, farm: Farm, ):
        # Needs other plants to grow
        if len(farm.plants) >= 2 and farm.environment == "pale":
            pass
        else:
            farm.plants.remove(self)

    def grow(self):
        # Grow moss on both sides
        if self.right_growing:
            self.image.blit(FarmAssets.moss_brush,
                            (self.x - self.rect.x + self.right_shift + random.choice([-4, 0, 4]), 444 - 252))

        if self.left_growing:
            self.image.blit(FarmAssets.moss_brush,
                            (self.x - self.rect.x - self.left_shift + random.choice([-4, 0, 4]), 444 - 252))


register_plant(PaleMoss)
