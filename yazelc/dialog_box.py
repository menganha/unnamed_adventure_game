import pygame

from yazelc import components as cmp
from yazelc import config as cfg
from yazelc import event_manager
from yazelc import zesper
from yazelc.controller import Controller, Button
from yazelc.event_type import EventType

WIDTH = cfg.RESOLUTION.x
HEIGHT = 50
SURFACE_DEPTH = 1900  # Above everything else but below the pause menu
X_MARGIN = 5
Y_MARGIN = 5
DELTA_LINE_SPACING = 7
TRIANGLE_VERTICES_1 = (WIDTH - 6, HEIGHT - 8)
TRIANGLE_VERTICES_2 = (WIDTH - 14, HEIGHT - 8)
TRIANGLE_VERTICES_3 = (WIDTH - 10, HEIGHT - 3)
DIALOG_FONT_ID = 'DIALOG'


def create_text_box(dialog_entity_id: int, dialog: cmp.Dialog, world: zesper.World):
    camera_pos = world.component_for_entity(world.camera_entity_id, cmp.Position)

    menu_pos_x = round(camera_pos.x)
    menu_pos_y = round(camera_pos.y + (cfg.RESOLUTION.y - HEIGHT))

    dialog.idle = False
    dialog.index = 0

    background = _create_surface_background()
    world.add_component(dialog_entity_id, cmp.Renderable(image=background, depth=SURFACE_DEPTH))
    world.add_component(dialog_entity_id, cmp.Position(menu_pos_x, menu_pos_y))
    world.add_component(dialog_entity_id, cmp.Input(handle_dialog_controllers))


def handle_dialog_controllers(entity_id: int, controller: Controller, world: zesper.World):
    dialog_ = world.component_for_entity(entity_id, cmp.Dialog)
    if controller.is_button_pressed(Button.A) and dialog_.idle:
        if dialog_.is_at_end():
            world.remove_component(entity_id, cmp.Renderable)
            world.remove_component(entity_id, cmp.Position)
            world.remove_component(entity_id, cmp.Input)
            dialog_.index = 0
            dialog_.index_start = 0
            event_manager.post_event(EventType.PAUSE)
        else:
            dialog_.idle = False
            surface = world.component_for_entity(entity_id, cmp.Renderable).image
            surface.fill(cfg.C_BLACK)


def add_triangle_signal(dialog_entity_id: int, world: zesper.World, color: pygame.Color = cfg.C_WHITE):
    """ Creates an entity that signals when the dialog has finished being written onto the dialog screen """
    dialog_renderable = world.component_for_entity(dialog_entity_id, cmp.Renderable)
    pygame.draw.polygon(dialog_renderable.image, color, [TRIANGLE_VERTICES_1, TRIANGLE_VERTICES_2, TRIANGLE_VERTICES_3])


def _create_surface_background() -> pygame.Surface:
    """ Creates and returns the Menu Image """
    surface = pygame.Surface((WIDTH, HEIGHT))
    surface.fill(cfg.C_BLACK)
    return surface
