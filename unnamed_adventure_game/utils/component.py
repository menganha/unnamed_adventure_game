""" Helper functions on components """

import unnamed_adventure_game.components as cmp


def position_of_unscaled_rect(hitbox: cmp.HitBox) -> (int, int):
    """
    Calculates the reference position of a rect before it has been scaled.
    Used mostly for hitboxes which normally are smaller than, e..g,  the containing sprite
    """
    x_pos = hitbox.rect.x + int(hitbox.scale_offset / 2)
    y_pos = hitbox.rect.y + int(hitbox.scale_offset / 2)
    return x_pos, y_pos
