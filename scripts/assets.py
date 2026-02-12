import os
import pygame

pygame.init()
screen = pygame.display.set_mode((1400, 800), pygame.RESIZABLE, pygame.SCALED)


class Assets:
    def __init__(self, pygame_: pygame):
        self.pygame = pygame_

    # Ui assets
    title = pygame.image.load(os.path.join("assets", "ui", "title.png")).convert_alpha()

    # Dev tools assets
    spacebar_command = pygame.image.load(os.path.join("assets", "ui", "dev", "test-dispenser.png")).convert_alpha()
    o_command = pygame.image.load(os.path.join("assets", "ui", "dev", "test-item.png")).convert_alpha()
    i_command = pygame.image.load(os.path.join("assets", "ui", "dev", "reset-items.png")).convert_alpha()
    l_command = pygame.image.load(os.path.join("assets", "ui", "dev", "delete-items.png")).convert_alpha()

    # Menu assets
    play_button_dark = pygame.image.load(os.path.join("assets", "ui", "menu", "play-dark.png")).convert()
    play_button_lit = pygame.image.load(os.path.join("assets", "ui", "menu", "play-lit.png")).convert()
    glitch_effect_off = pygame.image.load(os.path.join("assets", "ui", "menu", "glitch-effect-off.png")).convert_alpha()
    glitch_effect_on = pygame.image.load(os.path.join("assets", "ui", "menu", "glitch-effect-on.png")).convert_alpha()

    shooting_star_1 = pygame.image.load(
        os.path.join("assets", "decoration", "menu", "shooting-star-1.png")).convert_alpha()
    shooting_star_2 = pygame.image.load(
        os.path.join("assets", "decoration", "menu", "shooting-star-2.png")).convert_alpha()
    shooting_star_3 = pygame.image.load(
        os.path.join("assets", "decoration", "menu", "shooting-star-3.png")).convert_alpha()

    # Glitch effects [PRIMARY]
    energy_depleting_text = pygame.image.load(
        os.path.join("assets", "effects", "energy-depleting-text.png")).convert_alpha()

    # Glitch effects [SECONDARY]
    energy_depleting_glitching = pygame.image.load(os.path.join("assets", "effects", "secondary",
                                                                "energy-depleting-glitching.png")).convert_alpha()


class ItemAssets:
    # Item assets
    test_leaf = pygame.image.load(os.path.join("assets", "items", "test-leaf.png")).convert_alpha()
    energy_leaf = pygame.image.load(os.path.join("assets", "items", "energy-leaf.png")).convert_alpha()
    compressed_energy_leaves = pygame.image.load(
        os.path.join("assets", "items", "compressed-energy-leaves.png")).convert_alpha()
    lightbulb_fern_orb = pygame.image.load(
        os.path.join("assets", "items", "lightbulb-fern-orb.png")).convert_alpha()
    purified_lightbulb_fern_orb = pygame.image.load(
        os.path.join("assets", "items", "purified-lightbulb-fern-orb.png")).convert_alpha()
    recharger = pygame.image.load(os.path.join("assets", "items", "recharger", "recharger.png")).convert_alpha()
    recharger_2left = pygame.image.load(
        os.path.join("assets", "items", "recharger", "recharger-2left.png")).convert_alpha()
    recharger_1left = pygame.image.load(
        os.path.join("assets", "items", "recharger", "recharger-1left.png")).convert_alpha()
    depleted_recharger = pygame.image.load(os.path.join("assets", "items", "depleted-recharger.png")).convert_alpha()

    # Plant assets
    pale_moss_swathe = pygame.image.load(
        os.path.join("assets", "items", "pale-moss-swathe.png")).convert_alpha()
    light_bulb_fern_seed = pygame.image.load(
        os.path.join("assets", "items", "light-bulb-fern-seed.png")).convert_alpha()
    pale_bush_seed = pygame.image.load(
        os.path.join("assets", "items", "pale-bush-seed.png")).convert_alpha()

    # Air assets
    pale_air = pygame.image.load(os.path.join("assets", "items", "pale-air.png")).convert_alpha()
    pale_argon = pygame.image.load(os.path.join("assets", "items", "pale-argon.png")).convert_alpha()


class DispenserAssets:
    # Dispenser assets
    dispenser_closed = pygame.image.load(
        os.path.join("assets", "dispenser", "environment", "dispenser-closed.png")).convert_alpha()
    dispenser_open = pygame.image.load(
        os.path.join("assets", "dispenser", "environment", "dispenser-open.png")).convert_alpha()
    dispenser_shelf_down = pygame.image.load(
        os.path.join("assets", "dispenser", "environment", "dispenser-shelf-down.png")).convert_alpha()
    dispenser_shelf_transition = pygame.image.load(
        os.path.join("assets", "dispenser", "environment", "dispenser-shelf-transition.png")).convert_alpha()
    dispenser_shelf_up = pygame.image.load(
        os.path.join("assets", "dispenser", "environment", "dispenser-shelf-up.png")).convert_alpha()
    dispenser_energy_pipes = pygame.image.load(
        os.path.join("assets", "dispenser", "decoration", "energy-pipes.png")).convert_alpha()

    # Dispenser Ui
    dispenser_screen_off = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "dispenser-screen-off.png")).convert_alpha()
    dispenser_screen_on = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "dispenser-screen-on.png")).convert_alpha()

    drones_option_dark = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "options", "drones-option-dark.png")).convert_alpha()
    drones_option_lit = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "options", "drones-option-lit.png")).convert_alpha()
    fabricate_option_dark = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "options", "fabricate-option-dark.png")).convert_alpha()
    fabricate_option_lit = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "options", "fabricate-option-lit.png")).convert_alpha()
    storage_option_dark = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "options", "storage-option-dark.png")).convert_alpha()
    storage_option_lit = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "options", "storage-option-lit.png")).convert_alpha()
    processes_option_dark = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "options", "processes-option-dark.png")).convert_alpha()
    processes_option_lit = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "options", "processes-option-lit.png")).convert_alpha()
    farms_option_dark = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "options", "farms-option-dark.png")).convert_alpha()
    farms_option_lit = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "options", "farms-option-lit.png")).convert_alpha()

    drones_entry = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "entries", "drones-entry.png")).convert_alpha()
    fabricate_entry = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "entries", "fabricate-entry.png")).convert_alpha()
    storage_entry = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "entries", "storage-entry.png")).convert_alpha()
    processes_entry = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "entries", "processes-entry.png")).convert_alpha()
    farms_entry = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "entries", "farms-entry.png")).convert_alpha()
    environment_entry = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "entries", "environment-entry.png")).convert_alpha()

    connected_symbol = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "connected-symbol.png")).convert_alpha()

    wip = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "wip.png")).convert_alpha()

    four04 = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "404.png")).convert_alpha()

    # Arrows
    left_arrow = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "arrows", "left-arrow.png")).convert_alpha()
    left_arrow_lit = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "arrows", "left-arrow-lit.png")).convert_alpha()
    right_arrow = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "arrows", "right-arrow.png")).convert_alpha()
    right_arrow_lit = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "arrows", "right-arrow-lit.png")).convert_alpha()

    # Storage

    # Fabricate
    unlit_frame = pygame.image.load(os.path.join("assets", "recipes", "frame", "unlit-frame.png")).convert_alpha()
    lit_frame = pygame.image.load(os.path.join("assets", "recipes", "frame", "lit-frame.png")).convert_alpha()
    red_frame = pygame.image.load(os.path.join("assets", "recipes", "frame", "red-frame.png")).convert_alpha()

    # Processes
    fabrication_1 = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "processes", "fabrication-1.png")).convert_alpha()
    fabrication_1_lit = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "processes", "fabrication-1-lit.png")).convert_alpha()
    fabrication_2 = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "processes", "fabrication-2.png")).convert_alpha()
    fabrication_2_lit = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "processes", "fabrication-2-lit.png")).convert_alpha()
    fabrication_3 = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "processes", "fabrication-3.png")).convert_alpha()
    fabrication_3_lit = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "processes", "fabrication-3-lit.png")).convert_alpha()
    fabrication_4 = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "processes", "fabrication-4.png")).convert_alpha()
    fabrication_4_lit = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "processes", "fabrication-4-lit.png")).convert_alpha()
    fabrication_5 = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "processes", "fabrication-5.png")).convert_alpha()
    fabrication_5_lit = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "processes", "fabrication-5-lit.png")).convert_alpha()
    fabrication_6 = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "processes", "fabrication-6.png")).convert_alpha()
    fabrication_6_lit = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "processes", "fabrication-6-lit.png")).convert_alpha()

    # Farms
    farm_selection = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "farms", "farm-selection.png")).convert_alpha()
    selected_farm = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "farms", "selected-farm.png")).convert_alpha()
    disconnect_drone = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "farms", "disconnect-key.png")).convert_alpha()
    switch_entry = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "farms", "connect-key.png")).convert_alpha()
    plant_key = pygame.image.load(os.path.join("assets", "dispenser", "ui", "farms", "plant-key.png")).convert_alpha()
    item_display = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "farms", "item-display.png")).convert_alpha()

    # Frames
    farms_frame_lit = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "farms", "frame", "farms-frame-lit.png")).convert_alpha()
    farms_frame_unlit = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "farms", "frame", "farms-frame-unlit.png")).convert_alpha()
    farms_frame_red_x = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "farms", "frame", "farms-frame-red-x.png")).convert_alpha()
    # farms_frame_red_dark = pygame.image.load(
    #     os.path.join("assets", "dispenser", "ui", "farms", "frame", "farms-frame-red-dark.png")).convert_alpha()

    farms_selection_selected = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "farms", "selection-selected.png")).convert_alpha()

    # Environment
    lit_environment_frame = pygame.image.load(
        os.path.join("assets", "environ", "lit-environment-frame.png")).convert_alpha()

    # Controls
    control_drop = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "storage", "control-drop.png")).convert_alpha()

    # Item frame
    item_frame_bottom_left = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "frame", "item", "bottom-left-frame.png")).convert_alpha()
    item_frame_bottom_right = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "frame", "item", "bottom-right-frame.png")).convert_alpha()
    item_frame_top_left = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "frame", "item", "top-left-frame.png")).convert_alpha()
    item_frame_top_right = pygame.image.load(
        os.path.join("assets", "dispenser", "ui", "frame", "item", "top-right-frame.png")).convert_alpha()


class PlayerAssets:
    # Player assets
    player_left = pygame.image.load(os.path.join("assets", "player", "player-left.png")).convert_alpha()
    player_right = pygame.image.load(os.path.join("assets", "player", "player-right.png")).convert_alpha()

    # Player Ui
    energy_bar = pygame.image.load(os.path.join("assets", "ui", "interface", "energy-bar.png")).convert_alpha()


class GeneratorAssets:
    # Generator assets
    generator_default = pygame.image.load(
        os.path.join("assets", "generator", "environment", "generator-default.png")).convert_alpha()

    generator_input_1 = pygame.image.load(
        os.path.join("assets", "generator", "environment", "generator-input-1.png")).convert_alpha()

    generator_input_2 = pygame.image.load(
        os.path.join("assets", "generator", "environment", "generator-input-2.png")).convert_alpha()


class RoomAssets:
    # Room assets
    room_outline = pygame.image.load(os.path.join("assets", "environment", "room", "room-outline.png")).convert_alpha()


class FarmAssets:
    # Farm plot
    farm_box = pygame.image.load(os.path.join("assets", "farm", "farm-box.png")).convert_alpha()

    # Environment overlay
    pale_environment_overlay = pygame.image.load(
        os.path.join("assets", "farm", "environment-overlay", "pale.png")).convert_alpha()
    pale_environment_overlay.set_alpha(80)

    # Effect
    pale_cloud = pygame.image.load(os.path.join("assets", "farm", "effects", "pale-cloud.png")).convert_alpha()
    pale_cloud.set_alpha(10)
    grass = pygame.image.load(os.path.join("assets", "farm", "effects", "grass.png")).convert_alpha()
    grass_pixel_0 = pygame.image.load(os.path.join("assets", "farm", "effects", "grass-pixel-0.png")).convert_alpha()
    grass_pixel_1 = pygame.image.load(os.path.join("assets", "farm", "effects", "grass-pixel-1.png")).convert_alpha()
    grass_pixel_2 = pygame.image.load(os.path.join("assets", "farm", "effects", "grass-pixel-2.png")).convert_alpha()
    grass_pixel_3 = pygame.image.load(os.path.join("assets", "farm", "effects", "grass-pixel-3.png")).convert_alpha()
    grass_canvas = pygame.image.load(os.path.join("assets", "farm", "effects", "grass-canvas.png")).convert_alpha()

    # Ground
    dirt = pygame.image.load(os.path.join("assets", "farm", "ground", "dirt.png")).convert_alpha()
    pale_dirt = pygame.image.load(os.path.join("assets", "farm", "ground", "pale-dirt.png")).convert_alpha()

    # Plants
    test_plant = pygame.image.load(os.path.join("assets", "farm", "plants", "test-plant.png")).convert_alpha()
    blank_canvas = pygame.image.load(os.path.join("assets", "farm", "blank-canvas.png")).convert_alpha()

    # Pale Bush
    pale_leaf_1 = pygame.image.load(os.path.join("assets", "farm", "plants", "pale-bush", "leaf-1.png")).convert_alpha()
    pale_leaf_2 = pygame.image.load(os.path.join("assets", "farm", "plants", "pale-bush", "leaf-2.png")).convert_alpha()
    pale_leaf_3 = pygame.image.load(os.path.join("assets", "farm", "plants", "pale-bush", "leaf-3.png")).convert_alpha()
    pale_leaf_4 = pygame.image.load(os.path.join("assets", "farm", "plants", "pale-bush", "leaf-4.png")).convert_alpha()
    pale_leaf_5 = pygame.image.load(os.path.join("assets", "farm", "plants", "pale-bush", "leaf-5.png")).convert_alpha()
    pale_leaf_6 = pygame.image.load(os.path.join("assets", "farm", "plants", "pale-bush", "leaf-6.png")).convert_alpha()

    # Lightbulb Fern
    lightbulb_fern_branch = pygame.image.load(
        os.path.join("assets", "farm", "plants", "lightbulb-fern", "branch-segment.png")).convert_alpha()
    lightbulb_fern_stem = pygame.image.load(
        os.path.join("assets", "farm", "plants", "lightbulb-fern", "stem-segment.png")).convert_alpha()
    lightbulb_fern_pa_bulb_1 = pygame.image.load(
        os.path.join("assets", "farm", "plants", "lightbulb-fern", "pa-bulb-1.png")).convert_alpha()
    lightbulb_fern_pa_bulb_2 = pygame.image.load(
        os.path.join("assets", "farm", "plants", "lightbulb-fern", "pa-bulb-2.png")).convert_alpha()
    lightbulb_fern_pa_bulb_3 = pygame.image.load(
        os.path.join("assets", "farm", "plants", "lightbulb-fern", "pa-bulb-3.png")).convert_alpha()
    lightbulb_fern_tip = pygame.image.load(
        os.path.join("assets", "farm", "plants", "lightbulb-fern", "fern-tip.png")).convert_alpha()

    # Pale moss
    moss_brush = pygame.image.load(os.path.join("assets", "farm", "plants", "pale-moss", "moss.png")).convert_alpha()
    moss_brush.set_alpha(30)

    moss_flowers = pygame.image.load(
        os.path.join("assets", "farm", "plants", "pale-moss", "moss-flower.png")).convert_alpha()

    # Leaf brush
    leaf_brush_1 = pygame.image.load(os.path.join("assets", "farm", "plants", "leaf-brush-1.png")).convert_alpha()
    leaf_brush_2 = pygame.image.load(os.path.join("assets", "farm", "plants", "leaf-brush-2.png")).convert_alpha()
    leaf_brush_3 = pygame.image.load(os.path.join("assets", "farm", "plants", "leaf-brush-3.png")).convert_alpha()
    leaf_brush_4 = pygame.image.load(os.path.join("assets", "farm", "plants", "leaf-brush-4.png")).convert_alpha()
    leaf_brush_5 = pygame.image.load(os.path.join("assets", "farm", "plants", "leaf-brush-5.png")).convert_alpha()
    leaf_brush_6 = pygame.image.load(os.path.join("assets", "farm", "plants", "leaf-brush-6.png")).convert_alpha()


class KeyAssets:
    number_0 = pygame.image.load(os.path.join("assets", "ui", "numbers", "number-0.png")).convert_alpha()
    number_1 = pygame.image.load(os.path.join("assets", "ui", "numbers", "number-1.png")).convert_alpha()
    number_2 = pygame.image.load(os.path.join("assets", "ui", "numbers", "number-2.png")).convert_alpha()
    number_3 = pygame.image.load(os.path.join("assets", "ui", "numbers", "number-3.png")).convert_alpha()
    number_4 = pygame.image.load(os.path.join("assets", "ui", "numbers", "number-4.png")).convert_alpha()
    number_5 = pygame.image.load(os.path.join("assets", "ui", "numbers", "number-5.png")).convert_alpha()
    number_6 = pygame.image.load(os.path.join("assets", "ui", "numbers", "number-6.png")).convert_alpha()
    number_7 = pygame.image.load(os.path.join("assets", "ui", "numbers", "number-7.png")).convert_alpha()
    number_8 = pygame.image.load(os.path.join("assets", "ui", "numbers", "number-8.png")).convert_alpha()
    number_9 = pygame.image.load(os.path.join("assets", "ui", "numbers", "number-9.png")).convert_alpha()
    decimal = pygame.image.load(os.path.join("assets", "ui", "numbers", "decimal.png")).convert_alpha()
