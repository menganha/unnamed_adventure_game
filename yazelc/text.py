from pathlib import Path
from typing import Tuple, Optional

import pygame

pygame.font.init()
FONT_PATH = Path('assets', 'font', 'PressStart2P.ttf')
FONT_8 = pygame.font.Font(FONT_PATH, 8)
FONT_9 = pygame.font.Font(FONT_PATH, 9)


class Text:
    def __init__(self, text: str, size: int, color: pygame.Color):
        self.text = text
        if size == 8:
            self.font = FONT_8
        elif size == 9:
            self.font = FONT_9
        else:
            raise NotImplementedError(f'Font size {size} not available')
        self.size = self.font.size(text)
        self.surface = self.font.render(text, False, color)

    def render_at(self, target_surface: pygame.Surface, pos_x: Optional[int] = None, pos_y: Optional[int] = None):
        width, height = target_surface.get_size()
        center_x, center_y = self.get_coord_for_centered_surface(width, height)
        target_pos_x = pos_x if pos_x else center_x
        target_pos_y = pos_y if pos_y else center_y
        target_surface.blit(self.surface, (target_pos_x, target_pos_y))

    def get_coord_for_centered_surface(self, width: int, height: int) -> Tuple[int, int]:
        """
        Returns the position of the top-left corner of the rendered text surface such that it is centered in a rectangle
        of the input dimensions
        """
        coord_x = (-self.size[0] + width) // 2
        coord_y = (-self.size[1] + height) // 2
        return coord_x, coord_y
