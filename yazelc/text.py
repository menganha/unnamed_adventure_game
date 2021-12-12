from typing import Tuple, Optional

import pygame

from yazelc import resource_manager


class Text:
    FONT_NAME = 'Anonymous Pro'
    SPACE_CHAR = ' '

    def __init__(self, text: str, size: int = 11):
        self.text = text.rstrip()
        self.size = size
        self.font = resource_manager.get_resource(self.FONT_NAME)
        self.space_size = self.font.get_rect(self.SPACE_CHAR, size=self.size)
        self.avg_height = self.font.get_sized_height(self.size)

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

    def render_fitted_chunks(self, target_surface: pygame.Surface, color=pygame.Color, x_margin: int = 0, y_margin: int = 0,
                             delta_line_spacing: int = 2) -> bool:
        """ Renders text by chunks in the target surface until it depletes the text """

        if not self.text:  # If there is no more text then return that it is finished
            return True

        words = self.text.split(self.SPACE_CHAR)
        width, height = target_surface.get_size()
        x, y = x_margin, self.avg_height + y_margin
        cnt = 0
        for idx, word in enumerate(words):

            bounds = self.font.get_rect(word, size=self.size)
            if x + bounds.width + bounds.x >= width - x_margin:  # Jumps to the next line
                x, y = x_margin, y + self.avg_height + delta_line_spacing
            if x + bounds.width + bounds.x >= width - x_margin:
                raise ValueError("word too wide for the surface")
            if y + bounds.height - bounds.y >= height - y_margin:  # returns
                self.text = self.SPACE_CHAR.join(words[idx:])
                return False
            self.font.render_to(target_surface, (x, y), None, color, size=self.size)
            x += bounds.width + self.space_size.width
            cnt += 1
        self.text = self.SPACE_CHAR.join(words[cnt:])

        return False
