from pathlib import Path

import pygame


class ResourceManager:
    # TODO: HERE WE WOULD ALSO INITIALIZE THE SOUND RESOURCES
    TRUE_TYPE_FONT_FILETYPE = '.ttf'
    PNG_FILETYPE = '.png'

    def __init__(self):
        self._textures = {}
        self._fonts = {}

    def add_texture(self, path: Path, explicit_name: str = None):
        """ Uses file name stem if explicit name is not passed """
        name = path.stem if not explicit_name else explicit_name
        file_type = path.suffix
        if name not in self._textures:
            if file_type == self.PNG_FILETYPE:
                self._textures.update({name: pygame.image.load(path).convert_alpha()})
            else:
                raise ValueError(f'Unknown texture filetype: {path}')

    def add_font(self, path: Path, explicit_name: str = None):
        """ Uses file name stem if explicit name is not passed """
        name = path.stem if not explicit_name else explicit_name
        file_type = path.suffix
        if name not in self._fonts:
            if file_type == self.TRUE_TYPE_FONT_FILETYPE:
                font = pygame.freetype.Font(path)
                font.origin = True
                self._fonts.update({name: font})
            else:
                raise ValueError(f'Unknown font filetype: {path}')

    def get_texture(self, name: str):
        return self._textures[name]

    def get_font(self, name: str):
        return self._fonts[name]
