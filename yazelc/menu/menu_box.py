from typing import Callable

import pygame

from yazelc import components as cmp
from yazelc import config as cfg
from yazelc import event_manager
from yazelc import zesper
from yazelc.controller import Controller, Button
from yazelc.event_type import EventType

SURFACE_DEPTH = 2000  # Above everything else (1000 is the top map layer depth)
WIDTH = 130
TITLE_TEXT_POS_Y = 3
INITIAL_HEIGHT = 30
ROW_HEIGHT_INCREMENT = 10
ALPHA_INACTIVE = 150
INITIAL_ITEM_POS_Y = 25
ITEM_SEP_Y = 12
BG_COLOR = pygame.Color(cfg.C_BLACK.r, cfg.C_BLACK.g, cfg.C_BLACK.b, ALPHA_INACTIVE)
MENU_FONT_ID = 'MENU'


def create_death_menu(world: zesper.World):
    title = ''
    items = ['Save and Continue', 'Quit']
    font = world.resource_manager.get_font(MENU_FONT_ID)
    menu = cmp.Menu(title, items, font)

    def handle_death_menu_input(entity_id: int, controller: Controller, world_: zesper.World):
        menu_ = _update_menu(entity_id, controller, world_)
        if controller.is_button_pressed(Button.A):
            if menu_.item_idx_y == 0:
                world_.delete_entity(entity_id)
                event_manager.post_event(EventType.RESTART)
            elif menu_.item_idx_y == 1:
                quit_event = pygame.event.Event(pygame.QUIT)
                pygame.event.post(quit_event)

    _create_menu_box(menu, handle_death_menu_input, world)


def create_pause_menu(world: zesper.World):
    title = 'PAUSE'
    items = ['Continue', 'Quit']
    font = world.resource_manager.get_font(MENU_FONT_ID)
    menu = cmp.Menu(title, items, font)

    def handle_death_menu_input(entity_id: int, controller: Controller, world_: zesper.World):
        menu_ = _update_menu(entity_id, controller, world_)
        # Menu Logic
        if controller.is_button_pressed(Button.A):
            if menu_.item_idx_y == 0:
                event_manager.post_event(EventType.PAUSE)
                world.delete_entity(entity_id)
            elif menu_.item_idx_y == 1:
                quit_event = pygame.event.Event(pygame.QUIT)
                pygame.event.post(quit_event)
        elif controller.is_button_pressed(Button.START):
            event_manager.post_event(EventType.PAUSE)
            world.delete_entity(entity_id)

    _create_menu_box(menu, handle_death_menu_input, world)


def _create_menu_box(menu: cmp.Menu, input_function: Callable, world: zesper.World):
    camera_pos = world.component_for_entity(world.camera_entity_id, cmp.Position)

    height = INITIAL_HEIGHT + len(menu) * ROW_HEIGHT_INCREMENT
    menu_pos_x = round(camera_pos.x + (cfg.RESOLUTION.x - WIDTH) // 2)
    menu_pos_y = round(camera_pos.y + (cfg.RESOLUTION.y - height) // 2)

    surface = pygame.Surface((WIDTH, height), pygame.SRCALPHA)
    _refresh_menu_renderable(menu, surface)

    entity = world.create_entity()
    world.add_component(entity, cmp.Position(menu_pos_x, menu_pos_y))
    world.add_component(entity, menu)
    world.add_component(entity, cmp.Input(handle_input_function=input_function))
    world.add_component(entity, cmp.Renderable(image=surface, depth=SURFACE_DEPTH))


def _refresh_menu_renderable(menu: cmp.Menu, surface: pygame.Surface):
    """ Updates the menu image with the current selection """
    surface.fill(BG_COLOR)
    menu.font.render_text_at(menu.title, surface, pos_y=TITLE_TEXT_POS_Y)
    pos_y = INITIAL_ITEM_POS_Y
    for idx, text in enumerate(menu.items):
        alpha = None if idx == menu.item_idx_y else ALPHA_INACTIVE
        menu.font.render_text_at(text, surface, pos_y=pos_y, alpha=alpha)
        pos_y += ITEM_SEP_Y


def _update_menu(entity_id: int, controller: Controller, world: zesper.World) -> cmp.Menu:
    """ Updates the menu's selected item depending on the input """

    direction_x = - controller.is_button_down(Button.LEFT) + controller.is_button_down(Button.RIGHT)
    direction_y = - controller.is_button_down(Button.UP) + controller.is_button_down(Button.DOWN)

    menu = world.component_for_entity(entity_id, cmp.Menu)
    menu.item_idx_x += direction_x
    menu.item_idx_y += direction_y

    menu.item_idx_x = max(0, min(len(menu) - 1, menu.item_idx_x))
    menu.item_idx_y = max(0, min(len(menu) - 1, menu.item_idx_y))

    if direction_x | direction_y:
        image_surface = world.component_for_entity(entity_id, cmp.Renderable).image
        _refresh_menu_renderable(menu, image_surface)
    return menu
