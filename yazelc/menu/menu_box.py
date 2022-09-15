from typing import Callable

import pygame

from yazelc import components as cmp
from yazelc import config as cfg
from yazelc import zesper
from yazelc.controller import Button
from yazelc.event import PauseEvent, RestartEvent
from yazelc.systems.input_system import InputMessage

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
    _create_menu_box(menu, handle_death_menu_input, world)


def handle_death_menu_input(input_message: InputMessage):
    menu_ = _update_menu(input_message)
    if input_message.controller.is_button_pressed(Button.A):
        if menu_.item_idx_y == 0:
            input_message.world.delete_entity(input_message.ent_id)
            input_message.event_list.append(RestartEvent())
        elif menu_.item_idx_y == 1:
            quit_event = pygame.event.Event(pygame.QUIT)
            pygame.event.post(quit_event)


def create_pause_menu(world: zesper.World):
    title = 'PAUSE'
    items = ['Continue', 'Quit']
    font = world.resource_manager.get_font(MENU_FONT_ID)
    menu = cmp.Menu(title, items, font)
    _create_menu_box(menu, handle_pause_menu_input, world)


def handle_pause_menu_input(input_message: InputMessage):
    menu_ = _update_menu(input_message)
    # Menu Logic
    if input_message.controller.is_button_pressed(Button.A):
        if menu_.item_idx_y == 0:
            input_message.event_list.append(PauseEvent())
            input_message.world.delete_entity(input_message.ent_id)
        elif menu_.item_idx_y == 1:
            quit_event = pygame.event.Event(pygame.QUIT)
            pygame.event.post(quit_event)
    elif input_message.controller.is_button_pressed(Button.START):
        input_message.event_list.append(PauseEvent())
        input_message.world.delete_entity(input_message.ent_id)


def _create_menu_box(menu: cmp.Menu, input_function: Callable, world: zesper.World):
    height = INITIAL_HEIGHT + len(menu) * ROW_HEIGHT_INCREMENT
    menu_pos_x = round((cfg.RESOLUTION.x - WIDTH) // 2)
    menu_pos_y = round((cfg.RESOLUTION.y - height) // 2)

    surface = pygame.Surface((WIDTH, height), pygame.SRCALPHA)
    _refresh_menu_renderable(menu, surface)

    entity = world.create_entity()
    world.add_component(entity, cmp.Position(menu_pos_x, menu_pos_y, absolute=True))
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


def _update_menu(input_message: InputMessage) -> cmp.Menu:
    """ Updates the menu's selected item depending on the input """

    direction_x = - input_message.controller.is_button_down(Button.LEFT) + input_message.controller.is_button_down(Button.RIGHT)
    direction_y = - input_message.controller.is_button_down(Button.UP) + input_message.controller.is_button_down(Button.DOWN)

    menu = input_message.world.component_for_entity(input_message.ent_id, cmp.Menu)
    menu.item_idx_x += direction_x
    menu.item_idx_y += direction_y

    menu.item_idx_x = max(0, min(len(menu) - 1, menu.item_idx_x))
    menu.item_idx_y = max(0, min(len(menu) - 1, menu.item_idx_y))

    if direction_x | direction_y:
        image_surface = input_message.world.component_for_entity(input_message.ent_id, cmp.Renderable).image
        _refresh_menu_renderable(menu, image_surface)
    return menu
