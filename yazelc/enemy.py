from yazelc import components as cmp
from yazelc import zesper
from yazelc.systems.input_system import InputMessage
from yazelc.utils.game_utils import Direction, Status

JELLY_VEL = 0.5
JELLY_ID = 'jelly'
JELLY_SPRITE_WIDTH = 16
JELLY_ANIMATION_DELAY = 8


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
    world.add_component(enemy_entity, cmp.Animation(image_strip, delay=JELLY_ANIMATION_DELAY))
    world.add_component(enemy_entity, cmp.Renderable(image=image_strip[0]))
    world.add_component(enemy_entity, cmp.Input(handle_input_function=handle_input))
    return enemy_entity


def handle_input(input_message: InputMessage):
    state = input_message.world.component_for_entity(input_message.ent_id, cmp.State)
    velocity = input_message.world.component_for_entity(input_message.ent_id, cmp.Velocity)

    if state.status == Status.MOVING:
        velocity.x = state.direction.value.x
        velocity.y = state.direction.value.y
    else:
        velocity.x = 0
        velocity.y = 0

    if state.has_changed():
        image_strip = input_message.world.resource_manager.get_animation_strip(JELLY_ID)
        input_message.world.add_component(input_message.ent_id, cmp.Animation(image_strip, delay=JELLY_ANIMATION_DELAY))
