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


plant_ref = {}


def register_plant(plant):
    plant_ref[plant.name] = plant


def init_plant_rect(rect, x):
    rect.left = ((x - 224) // 204 * 204) + 228
    rect.bottom = 464


class Plant:
    """The parent class for all flora."""
    name = "plant"

    def __init__(self, x: int, environment: str):
        self.image = FarmAssets.blank_canvas.copy()
        self.rect = self.image.get_rect()

        self.rect.x = x
        init_plant_rect(self.rect, x)

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
        """Only modify when inheriting from a child of this class"""
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
    def wrapper(self, player, pressed_keys, pickup_ready, farm: Farm, dispenser):
        time_reduction_percent = 0

        for entry in farm.plants:
            if type(entry) == PaleMoss:
                time_reduction_percent += entry.flowers

        print(time_reduction_percent, "reduction")

        for i in range(len(self.cooldowns)):
            self.cooldowns[i] = self.cooldown_constants[i] - self.cooldown_constants[i] * (time_reduction_percent / 100)

        func(self, player, pressed_keys, pickup_ready, farm, dispenser)
        # self.grow_cooldown = self.GROW_COOLDOWN_CONST - self.GROW_COOLDOWN_CONST * (time_reduction_percent / 100)
        # self.bulb_move_cooldown = self.BULB_MOVE_CONST - self.BULB_MOVE_CONST * (time_reduction_percent / 100)

    return wrapper


class PaleBushPlant(Plant):
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

        # Cooldowns
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

        self.time_reduced = False

    def blit(self):
        screens["centered_display"].blit(self.image, self.rect)

    @pale_moss_synergy
    def update(self, player, pressed_keys, pickup_ready, farm: Farm, dispenser):
        # Grow the bush
        self.generate_cooldown = self.cooldowns[1]
        self.grow()

        self.generate_leaf_progress += clock.get_time()

        if not dispenser.stored_items.get("energy-leaf"):
            item_list = list(dispenser.stored_items.keys())
            item_list.sort()

            current_item = item_list[dispenser.current_item]

            dispenser.stored_items["energy-leaf"] = 0

            item_list = list(dispenser.stored_items.keys())
            item_list.sort()

            dispenser.current_item = item_list.index(current_item)


        if self.generate_cooldown <= 0:
            self.generate_cooldown = 1

        for _ in range(int(self.generate_leaf_progress // self.generate_cooldown)):
            dispenser.stored_items["energy-leaf"] += 1

        # 160.19 is the width

        # 0.005 po/second
        # 1 po from one leaf

        # self.generate_cooldown = 6000000 / self.width
        self.GENERATE_COOLDOWN_CONST = 6000000 / self.width

        self.cooldowns = [self.grow_cooldown, self.generate_cooldown]
        self.cooldown_constants = [self.GROW_COOLDOWN_CONST, self.GENERATE_COOLDOWN_CONST]

        self.generate_leaf_progress %= self.generate_cooldown

    @staticmethod
    def evaluate_output(farm: Farm):
        if farm.provided_items.get("pale-argon", None) is not None:
            farm.provided_items["pale-argon"] += 0.01 / (1000 / FARM_UPDATE_TICKS)
        else:
            farm.provided_items["pale-argon"] = 0.01 / (1000 / FARM_UPDATE_TICKS)

    def evaluate_input(self, farm):
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

        # if self.leaves:
        #     leaf_choice = random.choice(self.leaves)
        # else:
        #     leaf_choice = []

        if self.leaves:
            loc_x = random.randint(-int(self.width / 2), int(self.width / 2))
            loc_y = (((self.width / 2) ** 2) - (loc_x ** 2)) ** (1 / 2)

            # if abs(loc_x) >= 40:
            #     loc_x = (loc_x / abs(loc_x)) * 40

            if loc_x >= 40:
                loc_x = random.randint(24, 56)
                # loc_y = (((self.width / 2) ** 2) - (loc_x ** 2)) ** (1 / 2)

            if loc_x <= -40:
                loc_x = random.randint(-56, -24)

            loc = [(self.x - self.rect.x + loc_x) // 4 * 4, (212 - loc_y) // 4 * 4]

            # if abs((self.x - 228) - loc[0]) >= 40:
            #     if loc[0] != 0:
            #         loc[0] = (self.x - 228) + (loc[0] / abs(loc[0])) * 40
            #

        else:
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

        if self.leaves:
            for x in range(new_area.get_width()):
                for y in range(new_area.get_height()):
                    if new_area.get_at((x, y)).a == 255:
                        new_area.set_at((x, y), color)

        self.leaves.append(loc + [color])

        # if self.growing:
        #     self.overall_time += clock.get_time()

        if self.cooldown_progress >= self.grow_cooldown and self.growing:
            for _ in range(self.cooldown_progress // self.grow_cooldown):
                if random.random() < 0.0289:
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
                    for x in range(new_area.get_width()):
                        for y in range(new_area.get_height()):
                            if new_area.get_at((x, y)).a == 255:
                                new_area.set_at((x, y), "#979797")

                    pseudo_image = FarmAssets.blank_canvas.copy()
                    pseudo_image.blit(new_area, loc)
                    pseudo_image.blit(self.image, (0, 0))
                    self.image = pseudo_image
                    del pseudo_image

                if self.width < 160:
                    self.width += 0.2
                    self.height += 0.2
                else:
                    self.growing = False

            self.cooldown_progress %= self.grow_cooldown
        else:
            self.cooldown_progress += clock.get_time()

    def new_leaf(self, color, loc):
        # if abs(loc[0]) >= 40:
        #     loc[0] = 40 * (loc[0] / abs(loc[0]))

        loc_cop = copy.deepcopy(loc)

        new_area = random.choice([FarmAssets.leaf_brush_1, FarmAssets.leaf_brush_2, FarmAssets.leaf_brush_3,
                                  FarmAssets.leaf_brush_4, FarmAssets.leaf_brush_5, FarmAssets.leaf_brush_6])

        for x in range(new_area.get_width()):
            for y in range(new_area.get_height()):
                if new_area.get_at((x, y)).a == 255:
                    new_area.set_at((x, y), color)

        pseudo_image = FarmAssets.blank_canvas.copy()
        pseudo_image.blit(new_area, loc_cop)
        self.image.blit(pseudo_image, (0, 0))
        del pseudo_image

        # 348, 204

        # self.image.blit(new_area, loc)


register_plant(PaleBushPlant)


class LightBulbFern(Plant):
    name = "light-bulb-fern"

    def __init__(self, x: int, environment: str):
        super().__init__(x, environment)

        self.image = FarmAssets.blank_canvas.copy()
        self.bulb_positions = []
        self.branch_positions = []

        self.rect = self.image.get_rect()

        init_plant_rect(self.rect, x)
        self.x = x

        self.stem_y = 212
        self.stem_x = 0

        self.cooldown_progress = 0
        self.grow_cooldown = 10000  # 0.3 seconds
        self.GROW_COOLDOWN_CONST = 10000

        self.bulb_move_progress = 0
        self.bulb_move_cooldown = 80000
        self.BULB_MOVE_CONST = 80000

        # Cooldowns
        self.cooldowns = [self.grow_cooldown, self.bulb_move_cooldown]
        self.cooldown_constants = [self.GROW_COOLDOWN_CONST, self.BULB_MOVE_CONST]

        self.growing = True
        self.overall_time = 0  # Measure how long the plant grows for [DELETE LATER]

        self.bulb_stages = {1: FarmAssets.lightbulb_fern_pa_bulb_1, 2: FarmAssets.lightbulb_fern_pa_bulb_2,
                            3: FarmAssets.lightbulb_fern_pa_bulb_3}
        self.dispenser_ref = None

        self.time_reduced = False

    @pale_moss_synergy
    def update(self, player, pressed_keys, pickup_ready, farm: Farm, dispenser):
        self.dispenser_ref = dispenser

        self.grow()

        self.stem_x = self.x - farm.x

        self.blit()

        # self.grow_cooldown = self.cooldowns[0]
        # self.bulb_move_cooldown = self.cooldowns[1]

    def blit(self):
        bulb_image = self.image.copy()
        branch_image = self.image.copy()
        tip_image = self.image.copy()

        for bulb in self.bulb_positions:
            if bulb[2] <= 3:
                bulb_image.blit(self.bulb_stages[bulb[2]], bulb[:2])

        for branch in self.branch_positions:
            branch_image.blit(FarmAssets.lightbulb_fern_branch, branch)

        tip_image.blit(FarmAssets.lightbulb_fern_tip, (self.x - self.rect.x, self.stem_y + 244 - self.rect.y))

        screens["centered_display"].blit(self.image, self.rect)
        screens["centered_display"].blit(branch_image, self.rect)
        screens["centered_display"].blit(bulb_image, self.rect)
        screens["centered_display"].blit(tip_image, self.rect)

    @staticmethod
    def evaluate_output(farm: Farm):
        if farm.provided_items.get("pale-air", None) is not None:
            farm.provided_items["pale-air"] += 0.01 / (1000 / FARM_UPDATE_TICKS)
        else:
            farm.provided_items["pale-air"] = 0.01 / (1000 / FARM_UPDATE_TICKS)

    def evaluate_input(self, farm):
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
            self.overall_time += clock.get_time()

            if self.cooldown_progress >= self.grow_cooldown:
                for _ in range(self.cooldown_progress // self.grow_cooldown):
                    self.stem_y -= 4
                    self.image.blit(FarmAssets.lightbulb_fern_stem, (self.stem_x, self.stem_y))

                    if self.stem_y + 252 <= 464 - 4 * 26:
                        self.growing = False

                # if self.stem_y + 252 == 464 - 4 * 6:
                #     self.spawn_bulb()

                if (208 - self.stem_y - 4 * 6) % (7 * 4) == 0:
                    self.enrich_bulbs()
                    self.spawn_bulb()

                self.cooldown_progress %= self.grow_cooldown

            else:
                self.cooldown_progress += clock.get_time()

        else:
            if self.bulb_move_progress >= self.bulb_move_cooldown:
                for _ in range(self.bulb_move_progress // self.bulb_move_cooldown):
                    self.progress_bulbs()

                # if self.stem_y + 252 == 464 - 4 * 6:
                #     self.spawn_bulb()

                # if (208 - self.stem_y - 4 * 6) % (7 * 4) == 0:
                #     self.spawn_bulb()

                self.bulb_move_progress %= self.bulb_move_cooldown

            else:
                self.bulb_move_progress += clock.get_time()

    def spawn_bulb(self):
        outcomes = [0]
        self.bulb_positions.append(
            [self.stem_x - 20 + random.choice(outcomes), self.stem_y - 4 + random.choice(outcomes), 1])
        self.bulb_positions.append(
            [self.stem_x + 12 + random.choice(outcomes), self.stem_y - 4 + random.choice(outcomes), 1])

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
            bulb[2] += 1

            if bulb[0] < self.stem_x:
                bulb[0] -= 8

            elif bulb[0] > self.stem_x:
                bulb[0] += 4

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
        for bulb_idx in range(len(self.bulb_positions)):
            self.bulb_positions[bulb_idx][1] += 4
            if self.bulb_positions[bulb_idx][1] == 184:
                self.bulb_positions[bulb_idx] = ""

        grow_bulbs = False
        if "" in self.bulb_positions:
            grow_bulbs = True

        while "" in self.bulb_positions:
            self.bulb_positions.remove("")

            if self.dispenser_ref.stored_items.get("lightbulb-fern-orb"):
                self.dispenser_ref.stored_items["lightbulb-fern-orb"] += 1
            else:
                self.dispenser_ref.stored_items["lightbulb-fern-orb"] = 1

        for branch_idx in range(len(self.branch_positions)):
            self.branch_positions[branch_idx][1] += 4

            # TODO: Make the branches decay better
            if self.branch_positions[branch_idx][1] > 200 - (
                    abs((self.stem_x + 2) - self.branch_positions[branch_idx][0]) - 2):
                self.branch_positions[branch_idx] = ""

        while "" in self.branch_positions:
            self.branch_positions.remove("")

        if grow_bulbs:
            self.enrich_bulbs()

            for _ in range(6 - len(self.bulb_positions) // 2):
                self.spawn_bulb()


register_plant(LightBulbFern)


class PaleMoss(Plant):
    name = "pale-moss"

    def __init__(self, x, environment: str):
        print("pale mossing")
        super().__init__(x, environment)
        self.image = FarmAssets.blank_canvas.copy()
        self.flower_image = FarmAssets.blank_canvas.copy()
        self.rect = self.image.get_rect()

        self.x = x
        init_plant_rect(self.rect, x)

        self.left_shift = 0
        self.left_growing = True

        self.right_shift = 0
        self.right_growing = True

        self.shift_increment_progress = 0
        self.SHIFT_INCREMENT_COOLDOWN = 5000

        self.grow_progress = 0
        self.GROW_COOLDOWN = 1250

        self.flower_progress = 0
        self.FLOWER_COOLDOWN = 27500

        self.flowers = 0

        self.growing = True

    def blit(self):
        screens["centered_display"].blit(self.image, self.rect)
        screens["centered_display"].blit(self.flower_image, self.rect)

    def update(self, player, pressed_keys, pickup_ready, farm: Farm, dispenser):
        # print(self.rect, farm.x, self.x)

        # pygame.draw.rect(screens["centered_display"], "#FFFFFF", self.rect)

        self.shift_increment_progress += clock.get_time()
        self.grow_progress += clock.get_time()
        self.flower_progress += clock.get_time()

        for _ in range(self.grow_progress // self.GROW_COOLDOWN):
            # print(self.flowers, "flowers")
            self.grow()

        for _ in range(self.shift_increment_progress // self.SHIFT_INCREMENT_COOLDOWN):
            if self.x - self.rect.x - self.left_shift < farm.x:
                self.left_shift += 4
            else:
                self.left_growing = False

            if self.x - self.rect.x + self.right_shift < 196:
                self.right_shift += 4
            else:
                self.right_growing = False

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

        self.shift_increment_progress %= self.SHIFT_INCREMENT_COOLDOWN
        self.grow_progress %= self.GROW_COOLDOWN
        self.flower_progress %= self.FLOWER_COOLDOWN

    def evaluate_output(self, farm: Farm):
        pass

    def evaluate_input(self, farm: Farm, ):
        pass
        # if len(farm.plants) >= 2 and farm.environment == "pale":
        #     pass
        # else:
        #     farm.plants.remove(self)

    def grow(self):
        if self.right_growing:
            self.image.blit(FarmAssets.moss_brush,
                            (self.x - self.rect.x + self.right_shift + random.choice([-4, 0, 4]), 444 - 252))

        if self.left_growing:
            self.image.blit(FarmAssets.moss_brush,
                            (self.x - self.rect.x - self.left_shift + random.choice([-4, 0, 4]), 444 - 252))


register_plant(PaleMoss)
