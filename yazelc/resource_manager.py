import logging
from enum import Enum
from pathlib import Path

import pygame

from yazelc import animation
from yazelc.font import Font
from yazelc.utils.game_utils import Direction, Status


class SupportedFiletypes(Enum):
    TRUE_TYPE_FONT = '.ttf'
    PNG_FILETYPE = '.png'
    OGG_FILETYPE = '.ogg'


class ResourceManager:
    # TODO: HERE WE WOULD ALSO INITIALIZE THE SOUND RESOURCES
    TRUE_TYPE_FONT_FILETYPE = '.ttf'
    PNG_FILETYPE = '.png'
    OGG_FILETYPE = '.ogg'

    def __init__(self):
        self._textures = {}
        self._animation_stripes = {}
        self._fonts = {}
        self._sounds = {}
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
            return self.get_texture(name)

    def add_sound(self, path: Path, explicit_name: str = None) -> pygame.mixer.Sound:
        """ Uses file name stem if explicit name is not passed """
        name = path.stem if not explicit_name else explicit_name
        file_type = path.suffix
        if name not in self._sounds:
            if file_type == self.OGG_FILETYPE:
                sound = pygame.mixer.Sound(path)
                self._sounds.update({name: sound})
                return sound
            else:
                raise ValueError(f'Unknown sound filetype: {path}')
        else:
            logging.info(f'Sound on {path} has an existing Sound instance with the id {name}')
            self.get_sound(name)

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
                    self._pygame_font_objects.update({path: pygame.freetype.Font(path, size=size)})
                font = Font(self._pygame_font_objects[path], size, color)
                self._fonts.update({name: font})
                return font
            else:
                raise ValueError(f'Unknown font filetype: {path}')
        else:
            logging.info(f'Font on {path} has an existing instance with the id {name}')
            return self.get_font(name)

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

    def get_sound(self, name: str) -> pygame.mixer.Sound:
        return self._sounds[name]

    def get_animation_strip(self, name: str) -> list[pygame.Surface]:
        return self._animation_stripes[name]

    @staticmethod
    def get_animation_identifier(name_id: str, status: Status, direction: Direction = None) -> str:
        if direction:
            return f'{name_id}_{status.name}_{direction.name}'.lower()
        else:
            return f'{name_id}_{status.name}'.lower()

    def add_all_animation_strips(self, file_path: Path, name: str, sprite_width: int):
        """
        Expects file in the format name_<status>_<direction>.png and stores them in the name_<status>_<direction>. This is useful for
        moving characters (and possibly items) in the four directions.
        """

        for direction in (Direction.UP, Direction.DOWN, Direction.RIGHT, Direction.LEFT):
            flip = True if direction == Direction.LEFT else False
            direction_resource = Direction.RIGHT if direction == Direction.LEFT else direction
            for status in Status:
                identifier = self.get_animation_identifier(name, status, direction)
                img_path = file_path / (self.get_animation_identifier(name, status, direction_resource) + '.png')

                if not img_path.exists():
                    logging.info(f'The requested path for the animation strip {img_path} does not exists. Trying alternative...')
                    img_path = file_path / (self.get_animation_identifier(name, status) + '.png')
                    if not img_path.exists():
                        continue

                self.add_animation_strip(img_path, sprite_width, flip, identifier)

        # If no idle then use the first frame of the walking animation as a temporary solution
        has_idle = False
        for direction in (Direction.UP, Direction.DOWN, Direction.RIGHT, Direction.LEFT):
            status = Status.IDLE
            identifier = self.get_animation_identifier(name, status, direction)
            if identifier not in self._animation_stripes:
                walking_animation_id = self.get_animation_identifier(name, Status.WALKING, direction)
                if walking_animation_id not in self._animation_stripes:
                    continue
                strip = self.get_animation_strip(walking_animation_id)
                logging.info(f'No idle animation found for direction {direction.name}. '
                             f'Using the first frame of walking animation to replace it {walking_animation_id}')
                self._animation_stripes.update({identifier: strip[:1]})
                has_idle = True
            else:
                has_idle = True

        if not has_idle:
            logging.error(f'Could not get a replacement idle animation for animation {name} in {file_path}')
