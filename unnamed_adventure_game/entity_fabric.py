"""
The module gathers functions that add commonly used entities to an input world
"""
from pathlib import Path

import esper

import unnamed_adventure_game.components as cmp
from unnamed_adventure_game.animation_stripe import AnimationStripe
from unnamed_adventure_game.component_utils import position_of_unscaled_rect


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

    return player_entity


def create_jelly_at(x_pos: int, y_pos: int, world: esper.World):
    enemy_idle_down_image_path = Path('assets', 'sprites', 'enemy', 'jelly_idle.png')
    enemy_idle_animation = AnimationStripe(enemy_idle_down_image_path, sprite_width=16, delay=15)
    renderable = cmp.Renderable(image=enemy_idle_animation[0])
    weapon = cmp.Weapon(damage=1, active_frames=-1)
    enemy = cmp.EnemyTag
    position = cmp.Position(x=x_pos, y=x_pos)
    hitbox = cmp.HitBox(x_pos, y_pos, 16, 16)
    animation = cmp.Animation(enemy_idle_animation)
    health = cmp.Health()
    enemy_entity = world.create_entity(position, hitbox, animation, health, enemy, weapon, renderable)
    return enemy_entity
