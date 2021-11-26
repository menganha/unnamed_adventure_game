import esper
import pygame

from yazelc import components as cmp
from yazelc import config as cfg
from yazelc import event_manager
from yazelc import text
from yazelc.controller import Controller, Button
from yazelc.event_type import EventType
from yazelc.systems.camera_system import CameraSystem

# TODO: See if other types of menus, e.g., inventory menu have some emerging pattern that we can encapsulate on a
#  general class or module
WIDTH = 130
HEIGHT = 50
ALPHA = 150
BG_COLOR = pygame.Color(cfg.C_BLACK.r, cfg.C_BLACK.g, cfg.C_BLACK.b, ALPHA)
FG_COLOR = cfg.C_WHITE
FG_COLOR_INACTIVE = pygame.Color(cfg.C_WHITE.r, cfg.C_WHITE.g, cfg.C_WHITE.b, ALPHA)
PAUSE_TEXT = text.Text('PAUSE', size=8)
CONTINUE_TEXT = text.Text('Continue', size=8)
QUIT_TEXT = text.Text('Quit', size=8)
PAUSE_TEXT_POS_Y = 3
CONTINUE_TEXT_POS_Y = 25
QUIT_TEXT_POS_Y = 37


def create_base_surface():
    background = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    background.fill(BG_COLOR)
    PAUSE_TEXT.render_at(background, FG_COLOR, pos_y=PAUSE_TEXT_POS_Y)
    return background


def create_entity(world: esper.World):
    camera_entity = world.get_processor(CameraSystem).camera_entity
    camera_pos = world.component_for_entity(camera_entity, cmp.Position)

    menu_pos_x = round(-camera_pos.x + (cfg.RESOLUTION[0] - WIDTH) // 2)
    menu_pos_y = round(-camera_pos.y + (cfg.RESOLUTION[1] - HEIGHT) // 2)

    entity = world.create_entity()
    base_surface = create_base_surface()
    CONTINUE_TEXT.render_at(base_surface, FG_COLOR, pos_y=CONTINUE_TEXT_POS_Y)
    QUIT_TEXT.render_at(base_surface, FG_COLOR_INACTIVE, pos_y=QUIT_TEXT_POS_Y)
    world.add_component(entity, cmp.Renderable(image=base_surface))
    world.add_component(entity, cmp.Position(menu_pos_x, menu_pos_y))
    world.add_component(entity, cmp.Menu(0, 0, 0, 2))
    world.add_component(entity, cmp.Input(handle_input_function=handle_menu_input))


def handle_menu_input(entity: int, controller: Controller, world: esper.World):
    direction_x = - controller.is_button_down(Button.LEFT) + controller.is_button_down(Button.RIGHT)
    direction_y = - controller.is_button_down(Button.UP) + controller.is_button_down(Button.DOWN)

    menu = world.component_for_entity(entity, cmp.Menu)
    menu.item_x += direction_x
    menu.item_y += direction_y

    menu.item_x = max(0, min(menu.item_max_x - 1, menu.item_x))
    menu.item_y = max(0, min(menu.item_max_y - 1, menu.item_y))

    if direction_y and menu.item_y == 0:
        surface = create_base_surface()
        CONTINUE_TEXT.render_at(surface, FG_COLOR, pos_y=CONTINUE_TEXT_POS_Y)
        QUIT_TEXT.render_at(surface, FG_COLOR_INACTIVE, pos_y=QUIT_TEXT_POS_Y)
        world.component_for_entity(entity, cmp.Renderable).image = surface
    elif direction_y and menu.item_y == 1:
        surface = create_base_surface()
        CONTINUE_TEXT.render_at(surface, FG_COLOR_INACTIVE, pos_y=CONTINUE_TEXT_POS_Y)
        QUIT_TEXT.render_at(surface, FG_COLOR, pos_y=QUIT_TEXT_POS_Y)
        world.component_for_entity(entity, cmp.Renderable).image = surface

    if (controller.is_button_pressed(Button.A) and menu.item_y == 0) or controller.is_button_pressed(Button.START):
        event_manager.post_event(EventType.PAUSE)
        world.delete_entity(entity)
