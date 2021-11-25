from copy import copy
from pathlib import Path
from typing import List

import pygame


class AnimationStrip:
    """
    Parses an image strip containing different sprite states. The delay represent the amount of frames to wait until
    the next animation is loaded. If the frame_sequence is specified then this takes precedence and the delay input
    is ignored
    """

    def __init__(self, image_path: Path, sprite_width: int, delay: int = 1, frame_sequence: List[int] = None):
        self.strip = []
        self.delay = delay
        self.frame_sequence = frame_sequence

        # Parses the image
        image_stripe = pygame.image.load(image_path).convert_alpha()
        sprite_height = image_stripe.get_height()
        clipping_rect = pygame.Rect(0, 0, sprite_width, sprite_height)
        for idx in range(int(image_stripe.get_width() / sprite_width)):
            self.strip.append(image_stripe.subsurface(clipping_rect))
            clipping_rect.x += sprite_width

        # Constructs the frame sequence from delay input if this is not specified
        if not frame_sequence:
            self.frame_sequence = [idx for idx in range(len(self.strip)) for _ in range(self.delay)]

    def __getitem__(self, index):
        return self.strip[index]


def flip_strip_sprites(animation_strip: AnimationStrip, reverse_order: bool = True):
    """ Flips each stripe along the horizontal dimension """
    flipped_animation_strip = copy(animation_strip)
    if reverse_order:
        ordered_sprites = reversed(animation_strip.strip)
    else:
        ordered_sprites = animation_strip.strip
    flipped_animation_strip.strip = [pygame.transform.flip(sprite, flip_x=True, flip_y=False)
                                     for sprite in ordered_sprites]
    return flipped_animation_strip
