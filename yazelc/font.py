from typing import Tuple, Optional

import pygame


class Font:
    """ Wrapper around the pygame's freetype Fonts """

    SPACE_CHAR = ' '
    REFERENCE_CHAR = 'B'

    def __init__(self, font: pygame.freetype.Font, size: int, color: pygame.Color):
        font.origin = True
        self.font = font
        self.size = size
        self.color = color
        self.space_width = self.font.get_rect(self.SPACE_CHAR, size=self.size).width
        ref_char_rect = self.font.get_rect(self.REFERENCE_CHAR, size=self.size)
        self.char_width, self.char_height = ref_char_rect.width, ref_char_rect.height

    def render_text_at(self, text: str, target_surface: pygame.Surface, pos_x: Optional[int] = None, pos_y: Optional[int] = None,
                       alpha: int = None):
        width, height = target_surface.get_size()
        center_x, center_y = self.get_coord_for_centered_surface(text, width, height)
        target_pos_x = pos_x if pos_x else center_x
        target_pos_y = pos_y if pos_y else center_y
        if alpha:
            color_list = list(self.color)
            color_list[-1] = alpha
            actual_color = pygame.Color(*color_list)
        else:
            actual_color = self.color
        self.font.render_to(target_surface, (target_pos_x, target_pos_y), text, fgcolor=actual_color, size=self.size)

    def get_coord_for_centered_surface(self, text: str, width: int, height: int) -> Tuple[int, int]:
        """
        Returns the position of the top-left corner of the rendered text surface such that it is centered in a rectangle
        of the input dimensions
        """
        rect = self.get_rect(text)
        coord_x = (-rect.width + width) // 2
        coord_y = (-rect.height + height) // 2
        return coord_x, coord_y

    def get_rect(self, text) -> pygame.Rect:
        return self.font.get_rect(text, size=self.size)

    def render_fitted_word(self, text: str, target_surface: pygame.Surface, x_margin: int = 0, y_margin: int = 0,
                           delta_line_spacing: int = 7) -> bool:
        """ Renders text by chunks in the target surface until it depletes the text """
        words = text.split(self.SPACE_CHAR)
        width, height = target_surface.get_size()
        line_spacing = self.char_height + delta_line_spacing
        x, y = x_margin, self.char_height + y_margin
        for word in words:
            bounds = self.font.get_rect(word, size=self.size)
            if x + bounds.width + bounds.x >= width - x_margin:
                x, y = x_margin, y + line_spacing
            if x + bounds.width + bounds.x >= width - x_margin:
                raise ValueError("Word too wide for the surface")
            if y >= height - y_margin:
                return False
            self.font.render_to(target_surface, (x, y), None, self.color, size=self.size)
            x += bounds.width + self.space_width
        return True

    def fits_on_box(self, text: str, box_width: int):
        """ Checks if the sentence with the next word added in fits in the give width """
        bounds = self.font.get_rect(text, size=self.size)
        return bounds.width < box_width
