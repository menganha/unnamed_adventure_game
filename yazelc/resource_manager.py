from pathlib import Path

import pygame
import pygame.freetype

pygame.freetype.init()


# TODO: HERE WE WOULD ALSO INITIALIZE THE SOUND RESOURCES


class ResourceManager:
    TRUE_TYPE_FONT_FILETYPE = '.ttf'
    PNG_FILETYPE = '.png'

    def __init__(self):
        self.resources = {}

    def add_resource(self, path: Path, **options) -> object:
        name = path.stem
        file_type = path.suffix
        # Options depending on the file type/options
        if name not in self.resources:
            if file_type == self.TRUE_TYPE_FONT_FILETYPE:
                font = pygame.freetype.Font(path)
                font.antialiased = False
                self.resources.update({name: font})
            elif file_type == self.PNG_FILETYPE:
                self.resources.update({name: pygame.image.load(path).convert_alpha()})
        return self.resources[name]

    def get_resource(self, name: str):
        return self.resources[name]


_resource_manager = ResourceManager()


def add_resource(path: Path, **options) -> object:
    return _resource_manager.add_resource(path, **options)


def get_resource(name: str):
    return _resource_manager.get_resource(name)
