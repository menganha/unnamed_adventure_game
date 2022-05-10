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
DIALOG_FONT_COLOR = cfg.C_WHITE
X_MARGIN = 10
Y_MARGIN = 10


def create_dialog(interactive_entity_id, world: zesper.World):
    camera_pos = world.component_for_entity(world.camera_entity_id, cmp.Position)

    menu_pos_x = round(camera_pos.x)
    menu_pos_y = round(camera_pos.y + (cfg.RESOLUTION.y - HEIGHT))

    image_surface = _create_image_surface()
    text_string = world.component_for_entity(interactive_entity_id, cmp.Dialog).text.text
    dialog = cmp.Dialog(text_string)
    dialog.idle = dialog.text.render_fitted_word(image_surface, DIALOG_FONT_COLOR, X_MARGIN, Y_MARGIN)
    # TODO: Add some kind of blinking arrow

    dialog_entity_id = world.create_entity()
    world.add_component(dialog_entity_id, cmp.Renderable(image=image_surface, depth=SURFACE_DEPTH))
    world.add_component(dialog_entity_id, dialog)
    world.add_component(dialog_entity_id, cmp.Position(menu_pos_x, menu_pos_y))
    world.add_component(dialog_entity_id, cmp.Menu(0, 0, 0, 0))  # Just used for tagging purposes
    world.add_component(dialog_entity_id, cmp.Input(handle_dialog_controllers))


def handle_dialog_controllers(entity_id: int, controller: Controller, world: zesper.World):
    dialog_ = world.component_for_entity(entity_id, cmp.Dialog)
    if controller.is_button_pressed(Button.A) and dialog_.idle:
        if dialog_.text.is_empty():
            world.delete_entity(entity_id)
            event_manager.post_event(EventType.PAUSE)
        else:
            dialog_.idle = False
            surface = world.component_for_entity(entity_id, cmp.Renderable).image
            surface.fill(cfg.C_BLACK)


def _create_image_surface() -> pygame.Surface:
    """ Creates and returns the Menu Image """
    surface = pygame.Surface((WIDTH, HEIGHT))
    surface.fill(cfg.C_BLACK)
    return surface
