from pathlib import Path
from typing import Tuple, Optional

import pygame.freetype

pygame.freetype.init()


class Text:
    FONT_PATH = Path('assets', 'font', 'PressStart2P.ttf')
    FONT = pygame.freetype.Font(FONT_PATH)
    FONT.antialiased = False

    def __init__(self, text: str, size: int):
        self.text = text
        self.size = size
        self.rect = self.FONT.get_rect(text, size=size)

    def render_at(self, target_surface: pygame.Surface, fgcolor: pygame.Color, pos_x: Optional[int] = None, pos_y: Optional[int] = None):
        width, height = target_surface.get_size()
        center_x, center_y = self.get_coord_for_centered_surface(width, height)
        target_pos_x = pos_x if pos_x else center_x
        target_pos_y = pos_y if pos_y else center_y
        self.FONT.render_to(target_surface, (target_pos_x, target_pos_y), self.text, fgcolor=fgcolor, size=self.size)

    def get_coord_for_centered_surface(self, width: int, height: int) -> Tuple[int, int]:
        """
        Returns the position of the top-left corner of the rendered text surface such that it is centered in a rectangle
        of the input dimensions
        """
        coord_x = (-self.rect.width + width) // 2
        coord_y = (-self.rect.height + height) // 2
        return coord_x, coord_y
