import logging
from pathlib import Path

import pygame

from yazelc import animation
from yazelc.font import Font


class ResourceManager:
    # TODO: HERE WE WOULD ALSO INITIALIZE THE SOUND RESOURCES
    TRUE_TYPE_FONT_FILETYPE = '.ttf'
    PNG_FILETYPE = '.png'

    def __init__(self):
        self._textures = {}
        self._animation_stripes = {}
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
        else:
            logging.info(f'Image on {path} has an existing texture instance with the id {name}')
            self.get_texture(name)

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
        else:
            logging.info(f'Font on {path} has an existing instance with the id {name}')
            self.get_font(name)

    def add_animation_strip(self, path: Path, sprite_width: int, flip: bool = False, explicit_name: str = None) -> list[pygame.Surface]:
        """
        Assumes the passed image is a series of sprites depicting an animation, each with a width of <sprite_width>
        and ordered from left to right
        """
        texture = self.add_texture(path, explicit_name)
        name = path.stem if not explicit_name else explicit_name
        if name not in self._animation_stripes:
            strip = animation.get_frames_from_strip(texture, sprite_width)
            if flip:
                strip = animation.flip_strip_sprites(strip)
            self._animation_stripes.update({name: strip})
            return strip

    def add_animation_alias(self, name: str, alias: str):
        animation_strip = self.get_animation_strip(name)
        self._animation_stripes.update({alias: animation_strip})

    def get_texture(self, name: str) -> pygame.Surface:
        return self._textures[name]

    def get_font(self, name: str) -> Font:
        return self._fonts[name]

    def get_animation_strip(self, name: str) -> list[pygame.Surface]:
        return self._animation_stripes[name]
