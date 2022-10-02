import pygame


# class AnimationStrip:
#     """
#     Parses an image strip containing different sprite states. The delay represent the amount of frames to wait until
#     the next animation is loaded. If the frame_sequence is specified then this takes precedence and the delay input
#     is ignored
#     """
#
#     def __init__(self, image_stripe: pygame.Surface, sprite_width: int, delay: int = 1, frame_sequence: List[int] = None):
#         self.strip = []
#         self.delay = delay
#         self.frame_sequence = frame_sequence
#
#         # Parses the image
#         sprite_height = image_stripe.get_height()
#         clipping_rect = pygame.Rect(0, 0, sprite_width, sprite_height)
#         for idx in range(int(image_stripe.get_width() / sprite_width)):
#             self.strip.append(image_stripe.subsurface(clipping_rect))
#             clipping_rect.x += sprite_width
#
#         # Constructs the frame sequence from delay input if this is not specified
#         if not frame_sequence:
#             self.frame_sequence = [idx for idx in range(len(self.strip)) for _ in range(self.delay)]
#
#     def __getitem__(self, index):
#         return self.strip[index]

# TODO: Add alternative constructor that takes the strip as as set of images. This is actually more in line with
#  resource manager which could actually load images in set or strips of a subsurface. The problem we want to address
#  is to not regenerate subsurfaces. If this is not expensive then simply leave as it is


def get_frames_from_strip(image_stripe: pygame.Surface, sprite_width: int) -> list[pygame.Surface]:
    sprite_height = image_stripe.get_height()
    clipping_rect = pygame.Rect(0, 0, sprite_width, sprite_height)
    strip = []
    for idx in range(int(image_stripe.get_width() / sprite_width)):
        strip.append(image_stripe.subsurface(clipping_rect))
        clipping_rect.x += sprite_width
    return strip


def flip_strip_sprites(animation_strip: list[pygame.Surface], reverse_order: bool = False):
    """ Flips each stripe along the horizontal dimension """
    if reverse_order:
        ordered_sprites = reversed(animation_strip)
    else:
        ordered_sprites = animation_strip
    flipped_animation_strip = [pygame.transform.flip(sprite, flip_x=True, flip_y=False) for sprite in ordered_sprites]
    return flipped_animation_strip
