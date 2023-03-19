from typing import Optional

import pygame


class Font:
    """ Wrapper around the pygame's freetype Fonts """

    SPACE_CHAR = ' '
    REFERENCE_CHAR = 'B'
    DEFAULT_LINE_SPACING = 12

    def __init__(self, font: 'pygame.freetype.Font', size: int, color: pygame.Color):
        # font.origin = True
        self.font = font
        self.size = size
        self.color = color
        self.space_width = self.font.get_rect(self.SPACE_CHAR, size=self.size).width
        ref_char_rect = self.font.get_rect(self.REFERENCE_CHAR, size=self.size)
        self.char_width, self.char_height = ref_char_rect.width, ref_char_rect.height

    def render_text_at(self, text: str, target_surface: pygame.Surface, pos_x: Optional[int] = None, pos_y: Optional[int] = None,
                       alpha: int = None):
        """ If not explicitly provided, the routine will try to center the text on the texture surface """
        width, height = target_surface.get_size()
        center_x, center_y = self.get_coord_for_centered_surface(text, width, height)

        target_pos_x = center_x if pos_x is None else pos_x
        target_pos_y = center_y if pos_y is None else pos_y
        if alpha:
            color_list = list(self.color)
            color_list[-1] = alpha
            actual_color = pygame.Color(*color_list)
        else:
            actual_color = self.color
        self.font.render_to(target_surface, (target_pos_x, target_pos_y), text, fgcolor=actual_color, size=self.size)

    def render(self, text: str, center: bool = False) -> pygame.Surface:

        max_width, max_height, current_height = 0, 0, 0
        text_lines = text.splitlines()
        if len(text_lines) > 1:
            for line in text_lines:
                _, _, width, height = self.get_rect(line)
                height += current_height
                max_width = max(max_width, width)
                max_height = max(max_height, height)
                current_height += self.DEFAULT_LINE_SPACING
            surface = pygame.Surface((max_width, max_height))
            current_height = 0
            for line in text_lines:
                if center:
                    x = (max_width - self.get_rect(line).width) // 2
                else:
                    x = 0
                self.font.render_to(surface, (x, current_height), line, self.color, size=self.size)
                current_height += self.DEFAULT_LINE_SPACING
        else:
            surface, _ = self.font.render(text, fgcolor=self.color, size=self.size)

        return surface

    def get_coord_for_centered_surface(self, text: str, width: int, height: int) -> tuple[int, int]:
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
                           delta_line_spacing: int = None) -> bool:
        """ Renders text by chunks in the target surface until it depletes the text """
        words = text.split(self.SPACE_CHAR)
        width, height = target_surface.get_size()
        line_spacing = self.char_height + (delta_line_spacing if delta_line_spacing else self.DEFAULT_LINE_SPACING)
        x, y = x_margin, self.char_height + y_margin
        for word in words:
            bounds = self.get_rect(word)
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
