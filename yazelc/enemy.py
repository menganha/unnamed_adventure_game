from pathlib import Path

from yazelc import components as cmp
from yazelc import zesper
from yazelc.animation import AnimationStrip
from yazelc.controller import Controller

JELLY_VEL = 1


def create_jelly_at(x_pos: int, y_pos: int, world: zesper.World) -> int:
    enemy_idle_down_image_path = Path('assets', 'sprites', 'enemy', 'jelly_idle.png')
    enemy_idle_animation = AnimationStrip(enemy_idle_down_image_path, sprite_width=16, delay=15)
    enemy_entity = world.create_entity()
    world.add_component(enemy_entity, cmp.Brain(think_frames=50))
    world.add_component(enemy_entity, cmp.State())
    world.add_component(enemy_entity, cmp.Velocity())
    world.add_component(enemy_entity, cmp.Health())
    world.add_component(enemy_entity, cmp.Weapon(damage=1, active_frames=-1, freeze_frames=7, recoil_velocity=3))
    world.add_component(enemy_entity, cmp.HitBox(x_pos, y_pos, 16, 16))
    world.add_component(enemy_entity, cmp.Position(x=x_pos, y=x_pos))
    world.add_component(enemy_entity, cmp.EnemyTag())
    world.add_component(enemy_entity, cmp.Animation(enemy_idle_animation))
    world.add_component(enemy_entity, cmp.Renderable(image=enemy_idle_animation[0]))
    world.add_component(enemy_entity, cmp.Input(handle_input_function=handle_input))
    return enemy_entity


def handle_input(enemy_entity: int, controller: Controller, world: zesper.World):
    state = world.component_for_entity(enemy_entity, cmp.State)
    state.previous_status = state.status
    state.previous_direction = state.direction

    brain = world.component_for_entity(enemy_entity, cmp.Brain)
    velocity = world.component_for_entity(enemy_entity, cmp.Velocity)

    state.direction = brain.direction
    if state.direction:
        velocity.x = brain.direction.value.x
        velocity.y = brain.direction.value.y
    else:
        velocity.x = 0
        velocity.y = 0
