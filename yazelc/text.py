from typing import Tuple, Optional

import pygame

from yazelc import resource_manager


class Text:
    FONT_NAME = 'PressStart2P'

    def __init__(self, text: str, size: int = 8):
        self.text = text
        self.size = size
        self.font = resource_manager.get_resource(self.FONT_NAME)

    def render_at(self, target_surface: pygame.Surface, fg_color: pygame.Color, pos_x: Optional[int] = None, pos_y: Optional[int] = None):
        width, height = target_surface.get_size()
        center_x, center_y = self.get_coord_for_centered_surface(width, height)
        target_pos_x = pos_x if pos_x else center_x
        target_pos_y = pos_y if pos_y else center_y
        self.font.render_to(target_surface, (target_pos_x, target_pos_y), self.text, fgcolor=fg_color, size=self.size)

    def get_coord_for_centered_surface(self, width: int, height: int) -> Tuple[int, int]:
        """
        Returns the position of the top-left corner of the rendered text surface such that it is centered in a rectangle
        of the input dimensions
        """
        rect = self.get_rect()
        coord_x = (-rect.width + width) // 2
        coord_y = (-rect.height + height) // 2
        return coord_x, coord_y

    def get_rect(self):
        return self.font.get_rect(self.text, size=self.size)
