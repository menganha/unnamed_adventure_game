"""
The module gathers functions that add commonly used entities to an input world
"""
from pathlib import Path

import components as cmp
import esper
from animation_stripe import AnimationStripe


def create_player_at(x_pos: int, y_pos: int, world: esper.World) -> int:
    """ Creates basic player at the given position"""

    player_entity = world.create_entity()
    world.add_component(player_entity, cmp.Velocity(x=0, y=0))
    world.add_component(player_entity, cmp.Position(x=x_pos, y=y_pos))
    world.add_component(player_entity, cmp.Input())
    world.add_component(player_entity, cmp.Health())

    # Player Animations
    kwargs = {}
    for typ in ['idle', 'move', 'attack']:
        for direction in ['up', 'down', 'left']:
            img_path = Path('assets', 'sprites', 'player', f'{typ}_{direction}.png')
            delay = 4 if typ == 'attack' else 7
            kwargs.update({f'{typ}_{direction}': AnimationStripe(img_path, sprite_width=32, delay=delay)})

    world.add_component(player_entity, cmp.Renderable(image=kwargs['idle_down'][0]))
    world.add_component(player_entity, cmp.Animation(**kwargs))

    # Player HitBox
    sprite_width = kwargs['idle_down'][0].get_width()
    sprite_height = kwargs['idle_down'][0].get_height()
    scale_offset = - int(sprite_width * 0.50)
    world.add_component(player_entity, cmp.HitBox(x_pos, y_pos, sprite_width, sprite_height, scale_offset))

    return player_entity


def create_jelly_at(x_pos: int, y_pos: int, world: esper.World):
    enemy_entity = world.create_entity()
    enemy_idle_down_image_path = Path('assets', 'sprites', 'enemy', 'jelly_idle.png')
    enemy_idle_animation = AnimationStripe(enemy_idle_down_image_path, sprite_width=16, delay=15)
    world.add_component(enemy_entity, cmp.Renderable(image=enemy_idle_animation[0]))
    world.add_component(enemy_entity, cmp.Position(x=x_pos, y=x_pos))
    world.add_component(enemy_entity, cmp.HitBox(x_pos, y_pos, 16, 16))
    world.add_component(enemy_entity, cmp.Animation(enemy_idle_animation))
    world.add_component(enemy_entity, cmp.Health())
    return enemy_entity
