from yazelc import components as cmp
from yazelc import zesper
from yazelc.utils.game_utils import Direction, Status

JELLY_VEL = 0.5
JELLY_ID = 'jelly'
JELLY_SPRITE_WIDTH = 16
JELLY_ANIMATION_DELAY = 8

KEFER_ID = 'kefer'
KEFER_SPRITE_WIDTH = 16


def create_enemy_at(x_pos: int, y_pos: int, world: zesper.World, enemy_type: int) -> int:
    if enemy_type == 0:
        return create_jelly_at(x_pos, y_pos, world)
    elif enemy_type == 1:
        return create_kefer_at(x_pos, y_pos, world)
    else:
        raise RuntimeError(f'Unknown enemy type id {enemy_type}')


def create_jelly_at(x_pos: int, y_pos: int, world: zesper.World) -> int:
    image_strip = world.resource_manager.get_animation_strip(JELLY_ID)
    enemy_entity = world.create_entity()
    world.add_component(enemy_entity, cmp.Brain(think_frames=50))
    world.add_component(enemy_entity, cmp.Velocity())
    world.add_component(enemy_entity, cmp.Health())
    world.add_component(enemy_entity, cmp.Weapon(damage=1, active_frames=-1, freeze_frames=7, recoil_velocity=3))
    world.add_component(enemy_entity, cmp.HitBox(x_pos, y_pos, JELLY_SPRITE_WIDTH, JELLY_SPRITE_WIDTH))
    world.add_component(enemy_entity, cmp.Position(x=x_pos, y=y_pos))
    world.add_component(enemy_entity, cmp.EnemyTag())
    world.add_component(enemy_entity, cmp.State(Status.IDLE, Direction.DOWN))
    world.add_component(enemy_entity, cmp.Animation.from_delay(image_strip, JELLY_ANIMATION_DELAY))
    world.add_component(enemy_entity, cmp.Renderable(image=image_strip[0]))
    return enemy_entity


def create_kefer_at(x_pos: int, y_pos: int, world: zesper.World) -> int:
    image_strip = world.resource_manager.get_animation_strip('kefer_walking_down')
    enemy_entity = world.create_entity()
    world.add_component(enemy_entity, cmp.Brain(think_frames=50, behaviour_type=1))
    world.add_component(enemy_entity, cmp.Velocity())
    world.add_component(enemy_entity, cmp.Health())
    world.add_component(enemy_entity, cmp.Weapon(damage=1, active_frames=-1, freeze_frames=7, recoil_velocity=3))
    world.add_component(enemy_entity, cmp.HitBox(x_pos, y_pos, JELLY_SPRITE_WIDTH, JELLY_SPRITE_WIDTH))
    world.add_component(enemy_entity, cmp.Position(x=x_pos, y=y_pos))
    world.add_component(enemy_entity, cmp.EnemyTag())
    world.add_component(enemy_entity, cmp.State(Status.IDLE, Direction.DOWN))
    world.add_component(enemy_entity, cmp.Animation.from_delay(image_strip, JELLY_ANIMATION_DELAY))
    world.add_component(enemy_entity, cmp.Renderable(image=image_strip[0]))
    return enemy_entity
