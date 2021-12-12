from abc import ABC, abstractmethod
from typing import Tuple

import pygame

from yazelc import components as cmp
from yazelc import config as cfg
from yazelc import zesper
from yazelc.controller import Controller, Button
from yazelc.text import Text


# TODO: No need to create classes. We could pass some "base" functions as parameters to a "inherited" function
#   Class state variables could be stored in a component!
class BaseMenuCreator(ABC):
    """
    Creates translucent Menu with centered items
    """
    SURFACE_DEPTH = 2000  # Above everything else (1000 is the top map layer depth)
    WIDTH = 130
    TITLE_TEXT_POS_Y = 3
    INITIAL_HEIGHT = 30
    ROW_HEIGHT_INCREMENT = 10
    ALPHA = 150
    INITIAL_ITEM_POS_Y = 25
    ITEM_SEP_Y = 12
    BG_COLOR = pygame.Color(cfg.C_BLACK.r, cfg.C_BLACK.g, cfg.C_BLACK.b, ALPHA)
    FG_COLOR = cfg.C_WHITE
    FG_COLOR_INACTIVE = pygame.Color(cfg.C_WHITE.r, cfg.C_WHITE.g, cfg.C_WHITE.b, ALPHA)

    def __init__(self, title_text: str):
        self.menu_items = []
        self.height = self.INITIAL_HEIGHT
        self.title = Text(title_text)

    def add_menu_item(self, text: str):
        self.menu_items.append(Text(text))
        self.height += self.ROW_HEIGHT_INCREMENT

    @abstractmethod
    def handle_menu_input(self, entity: int, controller: Controller, world: zesper.World):
        pass

    def create_entity(self, world: zesper.World):
        camera_pos = world.component_for_entity(world.camera_entity_id, cmp.Position)

        menu_pos_x = round(camera_pos.x + (cfg.RESOLUTION.x - self.WIDTH) // 2)
        menu_pos_y = round(camera_pos.y + (cfg.RESOLUTION.y - self.height) // 2)

        base_surface = self._create_image_surface()

        entity = world.create_entity()
        world.add_component(entity, cmp.Renderable(image=base_surface, depth=self.SURFACE_DEPTH))
        world.add_component(entity, cmp.Position(menu_pos_x, menu_pos_y))
        world.add_component(entity, cmp.Menu(0, 0, 0, len(self.menu_items)))
        world.add_component(entity, cmp.Input(handle_input_function=self.handle_menu_input))

    def _create_image_surface(self, highlight_item_n: int = 0) -> pygame.Surface:
        """ Creates and returns the Menu Image """
        surface = pygame.Surface((self.WIDTH, self.height), pygame.SRCALPHA)
        surface.fill(BaseMenuCreator.BG_COLOR)
        self.title.render_at(surface, self.FG_COLOR, pos_y=self.TITLE_TEXT_POS_Y)
        pos_y = self.INITIAL_ITEM_POS_Y
        for idx, item in enumerate(self.menu_items):
            color = self.FG_COLOR if idx == highlight_item_n else self.FG_COLOR_INACTIVE
            item.render_at(surface, color, pos_y=pos_y)
            pos_y += self.ITEM_SEP_Y
        return surface

    @staticmethod
    def _handle_menu_controllers(entity_id: int, controller: Controller, world: zesper.World) -> Tuple[cmp.Menu, bool]:
        direction_x = - controller.is_button_down(Button.LEFT) + controller.is_button_down(Button.RIGHT)
        direction_y = - controller.is_button_down(Button.UP) + controller.is_button_down(Button.DOWN)

        menu = world.component_for_entity(entity_id, cmp.Menu)
        menu.item_x += direction_x
        menu.item_y += direction_y

        menu.item_x = max(0, min(menu.item_max_x - 1, menu.item_x))
        menu.item_y = max(0, min(menu.item_max_y - 1, menu.item_y))

        return menu, (direction_x | direction_y)
