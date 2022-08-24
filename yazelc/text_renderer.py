from typing import Tuple, Optional

import pygame

FONT_DEFAULT_SIZE = 11
SPACE_CHAR = ' '


def render_text_at(font: pygame.freetype.Font, text: str, target_surface: pygame.Surface, fg_color: pygame.Color,
                   pos_x: Optional[int] = None, pos_y: Optional[int] = None):
    width, height = target_surface.get_size()
    center_x, center_y = get_coord_for_centered_surface(font, text, width, height)
    target_pos_x = pos_x if pos_x else center_x
    target_pos_y = pos_y if pos_y else center_y
    font.render_to(target_surface, (target_pos_x, target_pos_y), text, fgcolor=fg_color, size=FONT_DEFAULT_SIZE)


def get_coord_for_centered_surface(font, text: str, width: int, height: int) -> Tuple[int, int]:
    """
    Returns the position of the top-left corner of the rendered text surface such that it is centered in a rectangle
    of the input dimensions
    """
    rect = get_rect(font, text)
    coord_x = (-rect.width + width) // 2
    coord_y = (-rect.height + height) // 2
    return coord_x, coord_y


def get_rect(font, text: str):
    return font.get_rect(text, size=FONT_DEFAULT_SIZE)


def render_fitted_word(font: pygame.freetype.Font, text: str, target_surface: pygame.Surface, color=pygame.Color, x_margin: int = 0,
                       y_margin: int = 0, delta_line_spacing: int = 7) -> bool:
    """ Renders text by chunks in the target surface until it depletes the text """
    # TODO: Should all of these variables be recalculated again and again everytime a new rendering is performed?
    #  Maybe store the "font" in a dataclass with all these variables on it?
    # TODO: Is there a way to only render the words that have not been rendered already? is it overoptimization?
    words = text.split(' ')
    width, height = target_surface.get_size()
    char_height = font.get_rect('B', size=FONT_DEFAULT_SIZE).height
    line_spacing = char_height + delta_line_spacing
    x, y = x_margin, char_height + y_margin
    space = font.get_rect(' ', size=FONT_DEFAULT_SIZE)
    for word in words:
        bounds = font.get_rect(word, size=FONT_DEFAULT_SIZE)
        if x + bounds.width + bounds.x >= width - x_margin:
            x, y = x_margin, y + line_spacing
        if x + bounds.width + bounds.x >= width - x_margin:
            raise ValueError("Word too wide for the surface")
        if y >= height - y_margin:
            return False
        font.render_to(target_surface, (x, y), None, color, size=FONT_DEFAULT_SIZE)
        x += bounds.width + space.width
    return True
