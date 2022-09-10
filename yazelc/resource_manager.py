from pathlib import Path

import pygame

from yazelc.font import Font


class ResourceManager:
    # TODO: HERE WE WOULD ALSO INITIALIZE THE SOUND RESOURCES
    TRUE_TYPE_FONT_FILETYPE = '.ttf'
    PNG_FILETYPE = '.png'

    def __init__(self):
        self._textures = {}
        self._fonts = {}
        self._pygame_font_objects = {}  # keeps track of pygame's loaded fonts (not the wrapper)

    def add_texture(self, path: Path, explicit_name: str = None) -> pygame.Surface:
        """ Uses file name stem if explicit name is not passed """
        name = path.stem if not explicit_name else explicit_name
        file_type = path.suffix
        if name not in self._textures:
            if file_type == self.PNG_FILETYPE:
                texture = pygame.image.load(path).convert_alpha()
                self._textures.update({name: texture})
                return texture
            else:
                raise ValueError(f'Unknown texture filetype: {path}')

    def add_font(self, path: Path, size: int, color: pygame.Color, explicit_name: str = None) -> Font:
        """
        Uses file name stem if explicit name is not passed

        Pygame's font objects are expensive to load. If we want to instantiate the same wrapper font instance
        with, e.g, different colors and sizes, then they will use the same reference to the pygame's freetype font
        """
        name = path.stem if not explicit_name else explicit_name
        file_type = path.suffix
        if name not in self._fonts:
            if file_type == self.TRUE_TYPE_FONT_FILETYPE:
                if path not in self._pygame_font_objects:
                    self._pygame_font_objects.update({path: pygame.freetype.Font(path)})
                font = Font(self._pygame_font_objects[path], size, color)
                self._fonts.update({name: font})
                return font
            else:
                raise ValueError(f'Unknown font filetype: {path}')

    def get_texture(self, name: str):
        return self._textures[name]

    def get_font(self, name: str):
        return self._fonts[name]
