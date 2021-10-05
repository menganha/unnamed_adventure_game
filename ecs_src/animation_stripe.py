from pathlib import Path

import pygame


class AnimationStripe:
    """
    Parses image containing a stripe of different sprite states to a helpful animation class. The delay
    represent the amount of frames to wait until the next animation is loaded
    """

    def __init__(self, image_path: Path, sprite_width: int, delay: int = 1, flip_x: bool = False, flip_y: bool = False):
        self.strip = []
        self.delay = delay

        self.delay_counter = 0
        self.current_image_index = 0

        self.image_path = image_path
        self.sprite_width = sprite_width

        image_stripe = pygame.transform.flip(pygame.image.load(image_path), flip_x, flip_y)
        sprite_height = image_stripe.get_height()
        clipping_rect = pygame.Rect(0, 0, sprite_width, sprite_height)
        for idx in range(int(image_stripe.get_width() / sprite_width)):
            self.strip.append(image_stripe.subsurface(clipping_rect))
            clipping_rect.x += sprite_width

    def next(self):
        """ Gets the next animation frame image"""
        current_image = self.strip[self.current_image_index]

        if self.delay_counter >= self.delay:
            self.current_image_index += 1
            self.delay_counter = 0
        self.delay_counter += 1

        if self.current_image_index == len(self.strip):
            self.current_image_index = 0
        return current_image

    def __getitem__(self, index):
        return self.strip[index]

    @classmethod
    def get_flipped_stripe(cls, animation_stripe: 'AnimationStripe', flip_x: bool, flip_y: bool):
        return cls(animation_stripe.image_path,
                   animation_stripe.sprite_width,
                   animation_stripe.delay,
                   flip_x,
                   flip_y)
