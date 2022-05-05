import pygame

from yazelc import event_manager
from yazelc import zesper
from yazelc.components import Renderable
from yazelc.controller import Controller, Button
from yazelc.event_type import EventType
from yazelc.menu.base_menu_creator import BaseMenuCreator


class PauseMenuCreator(BaseMenuCreator):
    TITLE_TEXT = 'PAUSE'
    CONTINUE_TEXT = 'Continue'
    QUIT_TEXT = 'Quit'

    def __init__(self):
        super().__init__(self.TITLE_TEXT)
        self.add_menu_item(self.CONTINUE_TEXT)
        self.add_menu_item(self.QUIT_TEXT)

    def handle_menu_input(self, entity: int, controller: Controller, world: zesper.World):
        menu, has_changed = self._handle_menu_controllers(entity, controller, world)

        if has_changed:
            image_surface = self._create_image_surface(menu.item_y)
            world.component_for_entity(entity, Renderable).image = image_surface

        # Menu Logic
        if controller.is_button_pressed(Button.A):
            if menu.item_y == 0:
                event_manager.post_event(EventType.PAUSE)
                world.delete_entity(entity)
            elif menu.item_y == 1:
                quit_event = pygame.event.Event(pygame.QUIT)
                pygame.event.post(quit_event)
        elif controller.is_button_pressed(Button.START):
            event_manager.post_event(EventType.PAUSE)
            world.delete_entity(entity)
