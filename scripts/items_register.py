# Create new items in this file, don't forget to register the file though!
import math
import random
from wsgiref.util import request_uri

from scripts.assets import ItemAssets
from scripts import plants_register
from scripts.plants_register import init_plant_rect

pickup_items = {}
items = []

# Items reference
items_ref = {
    # "item": Item,
    # "test-item": TestItem,
    # "energy-leaf": EnergyLeafItem,
    # "compressed-energy-leaves": CompressedEnergyLeavesItem,
    # "air": AirItem,
    # "pale-air": PaleAirItem,
    # "pale-argon": PaleArgonItem,
    # "lightbulb-fern-orb": LightbulbOrbItem,
    # "purified-lightbulb-fern-orb": PurifiedLightbulbFernOrbItem,
    # "pale-moss-swathe": PaleMossSwathe,
}

item_image_ref = {
    "item": ItemAssets.test_leaf,
    "test-item": ItemAssets.test_leaf,
    "energy-leaf": ItemAssets.energy_leaf,
    "compressed-energy-leaves": ItemAssets.compressed_energy_leaves,
    "air": ItemAssets.pale_air,
    "pale-air": ItemAssets.pale_air,
    "pale-argon": ItemAssets.pale_argon,
    "lightbulb-fern-orb": ItemAssets.lightbulb_fern_orb,
    "purified-lightbulb-fern-orb": ItemAssets.purified_lightbulb_fern_orb,
    "pale-moss-swathe": ItemAssets.pale_moss_swathe,
}


def register(pygame_module, clock_, **surfaces):
    global pygame
    global clock
    global screens

    pygame = pygame_module
    clock = clock_
    screens = surfaces


def register_item(item):
    items_ref[item.name] = item
    item_image_ref[item.name] = item.item_icon


# Parent class (Item)
class Item:
    """
    The parent class for all items
    REMEMBER TO OVERRIDE self.image AND self.name WITH THE IMAGE OF THE ITEM AND THE NAME OF THE ITEM RESPECTIVELY
    ALSO REMEMBER TO CALL self.init_rect AGAIN AFTER THE self.image
    """

    dispensable = True  # Can the item be dropped by the dispenser
    plantable = False  # Can the item be planted
    name = "item"  # The registry name of the item
    item_icon = ItemAssets.test_leaf  # The image used when stored in the dispenser
    storable = True  # Can the item be stored by the dispenser

    def __init__(self, x: int, y: int, has_gravity: bool):
        self.image = ItemAssets.test_leaf  # The image used when blit-ing
        self.rect = pygame.Rect(1, 1, 1, 1)  # Placeholder rect
        self.init_rect(x, y)

        self.gravity = 0
        self.floored = False
        self.has_gravity = has_gravity

    def blit(self):
        """Blit self.image onto the screen, generally don't override"""
        display_rect = pygame.rect.Rect((self.rect.x // 4) * 4, (self.rect.y // 4) * 4, self.rect.width,
                                        self.rect.height)
        screens["centered_display"].blit(self.image, display_rect)

    def update(self, player, pressed_keys, pickup_ready):
        """A basic update loop, override inject_update instead unless absolutely necessary"""
        self.update_floored()

        if self.has_gravity and not self.floored:
            self.rect.y += self.gravity
            self.gravity += (clock.get_time() / 1000) * (9.8 * 45)

        self.inject_update(player, pressed_keys, pickup_ready)

        self.update_floored()

        if self.floored and abs(player.rect.center[0] - self.rect.center[0]) < 32 + (self.image.get_width() / 2) and \
                pressed_keys[pygame.K_j] and pickup_ready and not player.dispenser_selected:
            pickup_items[abs(player.rect.center[0] - self.rect.center[0])] = self

        if self.floored:
            self.rect.y = 556 - self.rect.height

    def inject_update(self, player, pressed_keys, pickup_ready):
        """Override this when adding new update functionality to the item"""
        pass

    def update_floored(self):
        """Check if the item is floored"""
        if (self.rect.y + self.rect.height) >= 556 and not self.floored:
            self.floored = True

    def use(self, player):
        """Override every time. Return true to consume the item, and false to not.
         Add functionality before the return"""
        return False

    def fuel(self, generator):
        return False

    def init_rect(self, x, y):
        """Creates a rect for the item based on the image"""
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


# Parent class (Air/Environment Item)
class AirItem:
    dispensable = False
    plantable = False
    name = "air-item"
    item_icon = ItemAssets.pale_air
    storable = True

    def __init__(self):
        self.name = "air-item"
        self.image = ItemAssets.pale_air

    def update(self, player, pressed_keys, j_ready):
        items.remove(self)

    def blit(self):
        pass


class SeedItem:
    dispensable = False
    plantable = True
    name = "seed-item"
    item_icon = ItemAssets.pale_moss_swathe
    plant = "pale-bush"
    storable = True

    def __init__(self):
        self.image = ItemAssets.pale_air

    def update(self, player, pressed_keys, j_ready):
        items.remove(self)

    def blit(self):
        pass


# Test Item
class TestItem(Item):
    name = "test-item"
    item_icon = ItemAssets.test_leaf

    def __init__(self, x: int, y: int, has_gravity: bool):
        super().__init__(x, y, has_gravity)
        self.image = ItemAssets.test_leaf
        self.init_rect(x, y)
        self.x_shift = 0
        self.sin_shift = random.randint(-10, 10)
        self.orig_x = x

    def inject_update(self, player, pressed_keys, pickup_ready):
        self.x_shift = 0
        if not self.floored:
            self.rect.x = self.orig_x

        if self.has_gravity and self.rect.y < 552:
            self.gravity -= (clock.get_time() / 1000) * (9.7 * 45)

        # if self.has_gravity and self.gravity > 10:
        #     self.gravity = 10

        if not self.floored:
            self.x_shift = math.sin((pygame.time.get_ticks() / 200) + self.sin_shift) * 20
            self.rect.x += self.x_shift
            self.rect.x = (self.rect.x // 4) * 4

    def use(self, player):
        player.electricity += 3
        return True


register_item(TestItem)


# Energy Leaf Item
class EnergyLeafItem(Item):
    name = "energy-leaf"
    item_icon = ItemAssets.energy_leaf

    def __init__(self, x: int, y: int, has_gravity: bool):
        super().__init__(x, y, has_gravity)
        self.image = ItemAssets.energy_leaf

        self.init_rect(x, y)
        self.x_shift = 0
        self.sin_shift = random.randint(-10, 10)
        self.orig_x = x

    def inject_update(self, player, pressed_keys, pickup_ready):
        self.x_shift = 0
        if not self.floored:
            self.rect.x = self.orig_x

        if self.has_gravity and self.rect.y < 552:
            self.gravity -= (clock.get_time() / 1000) * (9.7 * 45)

        if self.has_gravity and self.gravity > 10:
            self.gravity = 10

        if not self.floored:
            self.x_shift = math.sin((pygame.time.get_ticks() / 200) + self.sin_shift) * 20
            self.rect.x += self.x_shift
            self.rect.x = (self.rect.x // 4) * 4

    def use(self, player):
        player.electricity += 3
        return True


register_item(EnergyLeafItem)


# Compressed Energy Leaves Item
class CompressedEnergyLeavesItem(Item):
    name = "compressed-energy-leaves"
    item_icon = ItemAssets.compressed_energy_leaves

    def __init__(self, x: int, y: int, has_gravity: bool):
        super().__init__(x, y, has_gravity)
        self.image = ItemAssets.compressed_energy_leaves
        self.init_rect(x, y)

    def inject_update(self, player, pressed_keys, pickup_ready):
        self.gravity -= (clock.get_time() / 1000) * (9.7 * 40)

    def use(self, player):
        return False

    def fuel(self, generator):
        # In lore, it's not 30 but 20 because the generator needs a stronger fuel to sustain itself
        # and only some of parts energy leaf can do that
        generator.electricity += 10
        return True


register_item(CompressedEnergyLeavesItem)


# Lightbulb orb
class LightbulbOrbItem(Item):
    name = "lightbulb-fern-orb"
    item_icon = ItemAssets.lightbulb_fern_orb

    def __init__(self, x: int, y: int, has_gravity: bool):
        super().__init__(x, y, has_gravity)
        self.image = ItemAssets.lightbulb_fern_orb
        self.init_rect(x, y)

    def inject_update(self, player, pressed_keys, pickup_ready):
        pass

    def use(self, player):
        return False


register_item(LightbulbOrbItem)


# Simple recharger
class SimpleRechargerItem(Item):
    """This is canonically a drink - EriX24"""
    name = "simple-recharger"
    item_icon = ItemAssets.recharger

    def __init__(self, x: int, y: int, has_gravity: bool):
        super().__init__(x, y, has_gravity)
        self.name = "simple-recharger"
        self.image = ItemAssets.recharger

        self.init_rect(x, y)

        self.uses = 3

    def use(self, player):
        player.electricity += 2

        if self.uses > 1:
            self.uses -= 1
            print(self.uses)
            return False

        index = player.items.index(self)
        depleted_version = DepletedRechargerItem(0, 0, True)
        player.items[index] = depleted_version

        return False

    # TODO: Make this a 3 use item that can be recharged


register_item(SimpleRechargerItem)


class DepletedRechargerItem(Item):
    name = "depleted-recharger"
    item_icon = ItemAssets.depleted_recharger

    def __init__(self, x: int, y: int, has_gravity: bool):
        super().__init__(x, y, has_gravity)
        self.name = "depleted-recharger"
        self.image = ItemAssets.depleted_recharger
        self.init_rect(x, y)


register_item(DepletedRechargerItem)


# Purified Lightbulb Fern Orb
class PurifiedLightbulbFernOrbItem(Item):
    name = "purified-lightbulb-fern-orb"
    item_icon = ItemAssets.purified_lightbulb_fern_orb

    def __init__(self, x: int, y: int, has_gravity: bool):
        super().__init__(x, y, has_gravity)
        self.image = ItemAssets.purified_lightbulb_fern_orb
        self.init_rect(x, y)
        self.name = "purified-lightbulb-fern-orb"

    def use(self, player):
        return False


register_item(PurifiedLightbulbFernOrbItem)


# Pale air
class PaleAirItem(AirItem):
    name = "pale-air"
    item_icon = ItemAssets.pale_air

    def __init__(self):
        super().__init__()
        self.name = "pale-air"
        self.image = ItemAssets.pale_air


register_item(PaleAirItem)


# Pale argon
class PaleArgonItem(AirItem):
    name = "pale-argon"
    item_icon = ItemAssets.pale_argon

    def __init__(self):
        super().__init__()
        self.name = "pale-argon"
        self.image = ItemAssets.pale_argon


register_item(PaleArgonItem)


# Pale moss swathe
class PaleMossSwathe(SeedItem):
    name = "pale-moss-swathe"
    item_icon = ItemAssets.pale_moss_swathe
    plant = "pale-moss"

    def __init__(self):
        self.name = "pale-moss-swathe"
        self.image = ItemAssets.pale_moss_swathe
        super().__init__()


register_item(PaleMossSwathe)


# Lightbulb fern seed
class LightBulbFernSeed(SeedItem):
    name = "light-bulb-fern-seed"
    item_icon = ItemAssets.light_bulb_fern_seed
    plant = "light-bulb-fern"

    def __init__(self):
        self.name = "light-bulb-fern-seed"
        self.image = ItemAssets.light_bulb_fern_seed
        super().__init__()


register_item(LightBulbFernSeed)


class PaleBushSeed(SeedItem):
    name = "pale-bush-seed"
    item_icon = ItemAssets.pale_bush_seed
    plant = "pale-bush"

    def __init__(self):
        self.name = "pale-bush-seed"
        self.image = ItemAssets.pale_bush_seed
        super().__init__()


register_item(PaleBushSeed)
