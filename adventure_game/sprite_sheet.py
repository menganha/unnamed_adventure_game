from pathlib import Path
from typing import Dict, List, Tuple

import pygame

from adventure_game.direction import Direction


class SpriteSheet:
    """
    Represents a sprite sheet. Each sprite sheet row represent a particular direction and the columns are
    the states of such animation.

    The convention is to have the rows of the sprite sheet ordered as follows: right, up, and down directions.

    If the spritesheet has less than three rows, the other directions will refer to the left direction sprites
    """

    def __init__(self, path: Path, sprite_size: Tuple[int, int]):
        self.path = path
        self.sprite_size = sprite_size
        self.image = pygame.image.load(path).convert_alpha()
        self.sprites: Dict[Direction, List[pygame.Surface]] = {}
        self._check_size_consistency()
        self.get_sprites()

    def get_sprites(self):
        """
        Loads all the sprites as subsurfaces and stores them in a dictionary where each key corresponds to a direction
        and the dictionary items are a list of subsurfaces representing the frames in the animation
        """
        num_of_directions = self.image.get_height() // self.sprite_size[1]
        previous_idx_y = 0
        for idx_y, direction in enumerate([Direction.LEFT, Direction.UP, Direction.DOWN]):
            self.sprites.update({direction: []})
            if idx_y + 1 > num_of_directions:
                row_idx = previous_idx_y
            else:
                row_idx = previous_idx_y = idx_y
            for idx_x in range(self.image.get_width() // self.sprite_size[0]):
                rect = pygame.Rect(idx_x * self.sprite_size[0], row_idx * self.sprite_size[1],
                                   self.sprite_size[0], self.sprite_size[1])
                self.sprites[direction].append(self.image.subsurface(rect))

        self.sprites[Direction.RIGHT] = self.sprites[Direction.LEFT]

    def _check_size_consistency(self):
        size = self.image.get_size()
        if size[0] % self.sprite_size[0] != 0 or size[1] % self.sprite_size[1] != 0:
            msg = 'Sprite sheet of size {} cannot be divided in squares of size {}'.format(size, self.sprite_size)
            raise ValueError(msg)
