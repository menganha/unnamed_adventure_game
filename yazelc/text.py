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
        self.avg_font_size = self.font.get_sized_height(self.size)
        self.x = self.y = None

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
        """
        Renders text by chunks in the target surface until it depletes the text
        TODO: Remove this unused method!
        """

        if not self.text:  # If there is no more text return that it has finished
            return True

        words = self.text.split(self.SPACE_CHAR)
        width, height = target_surface.get_size()
        x, y = x_margin, self.avg_font_size + y_margin
        word_count = 0
        for idx, word in enumerate(words):
            bounds = self.font.get_rect(word, size=self.size)
            if x + bounds.width + bounds.x >= width - x_margin:  # Jumps to the next line
                x, y = x_margin, y + self.avg_font_size + delta_line_spacing
            if x + bounds.width + bounds.x >= width - x_margin:
                raise ValueError("word too wide for the surface")
            if y + bounds.height - bounds.y >= height - y_margin:  # returns
                self.text = self.SPACE_CHAR.join(words[idx:])
                return False
            self.font.render_to(target_surface, (x, y), None, color, size=self.size)
            x += bounds.width + self.space_size.width
            word_count += 1
        self.text = self.SPACE_CHAR.join(words[word_count:])

        return False

    def render_fitted_word(self, target_surface: pygame.Surface, color=pygame.Color, x_margin: int = 0, y_margin: int = 0,
                           delta_line_spacing: int = 2) -> bool:
        """ Renders text by chunks in the target surface until it depletes the text """

        words = self.text.split(self.SPACE_CHAR)
        width, height = target_surface.get_size()

        if self.x and self.y:
            x, y = self.x, self.y
        else:
            x, y = x_margin, self.avg_font_size + y_margin

        bounds = self.font.get_rect(words[0], size=self.size)
        if x + bounds.width + bounds.x >= width - x_margin:  # Jumps to the next line
            x, y = x_margin, y + self.avg_font_size + delta_line_spacing
        if x + bounds.width + bounds.x >= width - x_margin:
            raise ValueError("Word too wide for the surface")
        if y + bounds.height - bounds.y >= height - y_margin:  # returns
            self.text = self.SPACE_CHAR.join(words)
            self.x, self.y = x_margin, self.avg_font_size + y_margin
            return True
        self.font.render_to(target_surface, (x, y), None, color, size=self.size)
        x += bounds.width + self.space_size.width

        self.x, self.y = x, y
        self.text = self.SPACE_CHAR.join(words[1:])

        if self.text:
            return False
        else:
            return True

    def is_empty(self):
        return not self.text
