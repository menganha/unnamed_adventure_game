import pygame

from adventure_game.animation_data import AnimationData
from adventure_game.direction import Direction
from adventure_game.sprite_sheet import SpriteSheet


class Animation:
    """
    Represents a particular animation for several directions
    """

    def __init__(self, sprite_sheet: SpriteSheet, animation_data: AnimationData):
        self.animation_data = animation_data
        self.sprite_sheet = sprite_sheet
        self.counter = 0

    def next_frame(self, direction: Direction) -> pygame.Surface:
        frame_data = self.animation_data.frame_index[direction]
        sprite_index = frame_data[self.counter]
        image = self.sprite_sheet.sprites[direction][sprite_index]
        if direction == Direction.RIGHT:
            image = pygame.transform.flip(image, True, False)

        self.counter += 1
        if self.counter >= len(frame_data):
            self.reset()

        return image

    def reset(self):
        self.counter = 0
