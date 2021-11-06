"""
The module gathers functions that add commonly used entities to an input world
"""
from pathlib import Path

import esper

import unnamed_adventure_game.components as cmp
from unnamed_adventure_game.animation_stripe import AnimationStripe
from unnamed_adventure_game.utils.component import position_of_unscaled_rect
from unnamed_adventure_game.utils.game import Direction


def create_player_at(center_x_pos: int, center_y_pos: int, world: esper.World) -> int:
    """ Creates the player entity centered at the given position"""

    player_entity = world.create_entity()
    # Animations
    kwargs = {}
    for typ in ['idle', 'move', 'attack']:
        for direction in ['up', 'down', 'left']:
            img_path = Path('assets', 'sprites', 'player', f'{typ}_{direction}.png')
            delay = 4 if typ == 'attack' else 7
            kwargs.update({f'{typ}_{direction}': AnimationStripe(img_path, sprite_width=32, delay=delay)})

    world.add_component(player_entity, cmp.Renderable(image=kwargs['idle_down'][0]))
    world.add_component(player_entity, cmp.Animation(**kwargs))

    # HitBox
    sprite_width = kwargs['idle_down'][0].get_width()
    sprite_height = kwargs['idle_down'][0].get_height()
    scale_offset = - int(sprite_width * 0.5)
    hitbox_component = cmp.HitBox(0, 0, sprite_width, sprite_height, scale_offset)
    hitbox_component.rect.centerx = center_x_pos
    hitbox_component.rect.centery = center_y_pos
    world.add_component(player_entity, hitbox_component)

    # Other components
    x_pos, y_pos = position_of_unscaled_rect(hitbox_component)
    world.add_component(player_entity, cmp.Position(x=x_pos, y=y_pos))
    world.add_component(player_entity, cmp.Velocity(x=0, y=0))
    world.add_component(player_entity, cmp.Input())
    world.add_component(player_entity, cmp.Health())
    world.add_component(player_entity, cmp.State())

    return player_entity


def create_melee_weapon(parent_hitbox: cmp.HitBox, direction: Direction, front_range: int, side_range: int,
                        damage: int, active_frames: int, world: esper.World) -> int:
    """ Creates a sword for the parent entity with a hitbox """

    if direction in (Direction.WEST, Direction.EAST):
        hitbox = cmp.HitBox(0, 0, front_range, side_range)
    else:
        hitbox = cmp.HitBox(0, 0, side_range, front_range)

    hitbox.rect.centerx = parent_hitbox.rect.centerx + int((parent_hitbox.rect.w + front_range) * direction.value.x) / 2
    hitbox.rect.centery = parent_hitbox.rect.centery + int((parent_hitbox.rect.h + front_range) * direction.value.y) / 2

    sword_ent = world.create_entity()
    world.add_component(sword_ent, hitbox)
    world.add_component(sword_ent, cmp.Weapon(damage=damage, active_frames=active_frames))
    world.add_component(sword_ent, cmp.Position(hitbox.rect.x, hitbox.rect.y))
    return sword_ent


def create_jelly_at(x_pos: int, y_pos: int, world: esper.World) -> int:
    enemy_idle_down_image_path = Path('assets', 'sprites', 'enemy', 'jelly_idle.png')
    enemy_idle_animation = AnimationStripe(enemy_idle_down_image_path, sprite_width=16, delay=15)
    enemy_entity = world.create_entity()
    world.add_component(enemy_entity, cmp.State())
    world.add_component(enemy_entity, cmp.Velocity())
    world.add_component(enemy_entity, cmp.Health())
    world.add_component(enemy_entity, cmp.Weapon(damage=1, active_frames=-1, freeze_frames=7, recoil_velocity=3))
    world.add_component(enemy_entity, cmp.HitBox(x_pos, y_pos, 16, 16))
    world.add_component(enemy_entity, cmp.Position(x=x_pos, y=x_pos))
    world.add_component(enemy_entity, cmp.EnemyTag())
    world.add_component(enemy_entity, cmp.Animation(enemy_idle_animation))
    world.add_component(enemy_entity, cmp.Renderable(image=enemy_idle_animation[0]))
    return enemy_entity
