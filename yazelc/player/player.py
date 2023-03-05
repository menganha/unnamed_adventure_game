"""
The module gathers functions that add commonly used entities to an input world
"""

from yazelc import components as cmp
from yazelc import config as cfg
from yazelc import weapons
from yazelc import zesper
from yazelc.controller import Button
from yazelc.event.events import InputEvent, ExplosionEvent, BlockInputEvent, DeleteEntityEvent, SoundTriggerEvent
from yazelc.utils.game_utils import Direction, Status

VELOCITY = 1.5 - 1e-8  # This ensures that the rounding produces the displacement pattern 1,2,1,2... that averages a velocity of 1.5
VELOCITY_DIAGONAL = 1

HITBOX_HEIGHT = 10
HITBOX_WIDTH = 10
HITBOX_Y_OFFSET = 2
SKIN_DEPTH = 5
SPRITE_SIZE = 16
SPRITE_DEPTH = 200

MAX_HEALTH = 10  # Should always be divisible by two

ATTACK_ANIMATION_DELAY = 4
IDLE_ANIMATION_FRAME = 10
MOVE_ANIMATION_DELAY = 5

# TODO: Modify the sprite such that the range of the sword is the same on all cardinal directions!!!
SWORD_FRONT_RANGE = 15
SWORD_SIDE_RANGE = 20
SWORD_FREEZE_FRAMES = 15
SWORD_DAMAGE = 5
SWORD_ACTIVE_FRAMES = ATTACK_ANIMATION_DELAY * 4
SWORD_RECOIL_VEL = 5
SWORD_SPRITE_WIDTH = 48
SWORD_SOUND_EFFECT = 'hit'

INTERACTIVE_FRONT_RANGE = 10
INTERACTIVE_SIDE_RANGE = 2



def create_player_at(center_x_pos: int, center_y_pos: int, world: zesper.World) -> int:
    """ Creates the player entity centered at the given position"""

    player_entity_id = world.create_entity()
    stripe = world.resource_manager.get_animation_strip(f'{Status.IDLE.name}_{Direction.DOWN.name}')
    world.add_component(player_entity_id, cmp.Renderable(stripe[0], depth=SPRITE_DEPTH))
    # world.add_component(player_entity_id, cmp.Animation(stripe[:1], delay=IDLE_ANIMATION_FRAME))

    # HitBox
    hitbox_component = cmp.HitBox(0, 0, HITBOX_WIDTH, HITBOX_HEIGHT, skin_depth=SKIN_DEPTH)
    hitbox_component.center = (center_x_pos, center_y_pos)
    world.add_component(player_entity_id, hitbox_component)

    # Other components
    x_pos, y_pos = get_position_of_sprite(hitbox_component)
    world.add_component(player_entity_id, cmp.Position(x=x_pos, y=y_pos))
    world.add_component(player_entity_id, cmp.Velocity(x=0, y=0))
    world.add_component(player_entity_id, cmp.State(Status.IDLE, Direction.DOWN))
    world.add_component(player_entity_id, cmp.Health(points=MAX_HEALTH))
    return player_entity_id


def get_position_of_sprite(hitbox: cmp.HitBox):
    """ Gets the position of the sprite from the player's Hitbox """
    relative_pos_x = SPRITE_SIZE // 2
    relative_pos_y = SPRITE_SIZE // 2 + HITBOX_Y_OFFSET
    return hitbox.centerx - relative_pos_x, hitbox.centery - relative_pos_y


def get_position_of_hitbox(sprite_position: cmp.Position):
    """ Gets the position of the center hitbox from the player's position """
    relative_pos_x = SPRITE_SIZE // 2
    relative_pos_y = SPRITE_SIZE // 2 + HITBOX_Y_OFFSET
    return sprite_position.x + relative_pos_x, sprite_position.y + relative_pos_y


def drop_bomb(player_entity_id: int, world: zesper.World):
    position = world.component_for_entity(player_entity_id, cmp.Position)
    direction = world.component_for_entity(player_entity_id, cmp.State).direction
    renderable = world.component_for_entity(player_entity_id, cmp.Renderable)

    bomb_position_center_x = position.x + renderable.width // 2 + direction.value.x * 8
    bomb_position_center_y = position.y + renderable.height // 2 + direction.value.y * 8
    bomb_position = cmp.Position(bomb_position_center_x - weapons.BOMB_SPRITE_WIDTH // 2,
                                 bomb_position_center_y - weapons.BOMB_SPRITE_WIDTH // 2)

    weapons.create_bomb(bomb_position, world)


def create_melee_weapon(player_entity_id: int, world: zesper.World):
    """ Creates a Weapon hitbox for the parent entity with a hitbox """
    weapon_entity_id = _create_hitbox_in_front(player_entity_id, SWORD_FRONT_RANGE, SWORD_SIDE_RANGE, world)
    world.add_component(weapon_entity_id,
                        cmp.Weapon(damage=SWORD_DAMAGE, active_frames=SWORD_ACTIVE_FRAMES, freeze_frames=SWORD_FREEZE_FRAMES,
                                   recoil_velocity=SWORD_RECOIL_VEL))

    direction = world.component_for_entity(player_entity_id, cmp.State).direction
    strip = world.resource_manager.get_animation_strip(f'wooden_sword_{direction.name}')
    world.add_component(weapon_entity_id, cmp.Animation.from_delay(strip, ATTACK_ANIMATION_DELAY, one_loop=True))
    world.add_component(weapon_entity_id, cmp.Renderable(strip[0], SPRITE_DEPTH + 1))
    player_position = world.component_for_entity(player_entity_id, cmp.Position)
    weapon_position_x = player_position.x - (SWORD_SPRITE_WIDTH - SPRITE_SIZE) // 2
    weapon_position_y = player_position.y - (SWORD_SPRITE_WIDTH - SPRITE_SIZE) // 2
    world.add_component(weapon_entity_id, cmp.Position(weapon_position_x, weapon_position_y))


def create_interactive_hitbox(player_entity_id: int, world: zesper.World):
    """ Creates a hitbox to detect interaction with other objects """
    entity_id = _create_hitbox_in_front(player_entity_id, INTERACTIVE_FRONT_RANGE, INTERACTIVE_SIDE_RANGE, world)
    world.add_component(entity_id, cmp.InteractorTag())
    world.event_queue.enqueue_event(DeleteEntityEvent(entity_id), frames_delay=1)


def handle_animation_for_input(ent_id: int, state: cmp.State, world: zesper.World):
    animation_identifier = f'{state.status.name}_{state.direction.name}'
    strip = world.resource_manager.get_animation_strip(animation_identifier)

    if state.status == Status.IDLE:
        strip = strip[:1]
        animation_frames = 1
    elif state.status.MOVING:
        animation_frames = MOVE_ANIMATION_DELAY
    elif state.status.ATTACKING:
        animation_frames = ATTACK_ANIMATION_DELAY
    else:
        raise RuntimeError(f'Animation frame for player not specified for the status {state.status} and direction {state.direction}')

    world.add_component(ent_id, cmp.Animation.from_delay(strip, animation_frames))


def handle_input(input_event: InputEvent, player_entity_id: int, world: zesper.World):
    velocity = world.component_for_entity(player_entity_id, cmp.Velocity)
    position = world.component_for_entity(player_entity_id, cmp.Position)

    direction_x = - input_event.controller.is_button_down(Button.LEFT) + input_event.controller.is_button_down(Button.RIGHT)
    direction_y = - input_event.controller.is_button_down(Button.UP) + input_event.controller.is_button_down(Button.DOWN)

    abs_vel = VELOCITY_DIAGONAL if (direction_y and direction_x) else VELOCITY
    velocity.x = direction_x * abs_vel
    velocity.y = direction_y * abs_vel

    # Snaps position to grid when the respective key has been released.  This allows for a deterministic movement
    # pattern by eliminating any decimal residual accumulated when resetting the position to an integer value
    horizontal_key_released = (input_event.controller.is_button_released(Button.LEFT) or
                               input_event.controller.is_button_released(Button.RIGHT))
    vertical_key_released = (input_event.controller.is_button_released(Button.UP) or
                             input_event.controller.is_button_released(Button.DOWN))

    if horizontal_key_released:
        position.x = round(position.x)
    if vertical_key_released:
        position.y = round(position.y)

    # Attempt to change direction only when a key is released or the status of the entity is not moving
    state = world.component_for_entity(player_entity_id, cmp.State)
    state.update()

    if (horizontal_key_released or vertical_key_released) or state.status != Status.MOVING:  # If it's moving don't change directions
        if direction_x > 0:
            state.direction = Direction.RIGHT
        elif direction_x < 0:
            state.direction = Direction.LEFT
        if direction_y > 0:
            state.direction = Direction.DOWN
        elif direction_y < 0:
            state.direction = Direction.UP

    if input_event.controller.is_button_pressed(Button.B):
        state.status = Status.ATTACKING
    elif not direction_x and not direction_y:
        state.status = Status.IDLE
    else:
        state.status = Status.MOVING

    if state.has_changed():
        handle_animation_for_input(player_entity_id, state, world)

    if input_event.controller.is_button_pressed(Button.B):
        velocity.x = 0  # Stop player when is attacking
        velocity.y = 0

        # TODO: one should create a small delay until the actual hitbox is created as the attack animation has some
        #   of gaining momentum for the swing
        # Creates a temporary hitbox representing the sword weapon
        create_melee_weapon(player_entity_id, world)

        # Block input until weapon lifetime is over and publish attach event. We need to block it one frame less than
        # the number of active frames as we are counting already the frame when it is activated as active
        sound_trigger_event = SoundTriggerEvent(SWORD_SOUND_EFFECT)
        block_event = BlockInputEvent(SWORD_ACTIVE_FRAMES - 1)
        world.event_queue.enqueue_event(sound_trigger_event)
        world.event_queue.enqueue_event(block_event)

    if input_event.controller.is_button_pressed(Button.A):
        create_interactive_hitbox(player_entity_id, world)

    if input_event.controller.is_button_pressed(Button.L):
        explosion_event = ExplosionEvent(position, 30, 30, cfg.C_WHITE)
        world.event_queue.enqueue_event(explosion_event)

    if input_event.controller.is_button_pressed(Button.X):
        drop_bomb(player_entity_id, world)

    if input_event.controller.is_button_pressed(Button.SELECT):
        cfg.DEBUG_MODE = not cfg.DEBUG_MODE


def _create_hitbox_in_front(player_entity_id: int, front_range: int, side_range: int, world: zesper.World) -> int:
    """ Creates a hitbox in the direction the player is facing """
    direction = world.component_for_entity(player_entity_id, cmp.State).direction
    if direction in (Direction.LEFT, Direction.RIGHT):
        hitbox = cmp.HitBox(0, 0, front_range, side_range)
    else:
        hitbox = cmp.HitBox(0, 0, side_range, front_range)

    player_hitbox = world.component_for_entity(player_entity_id, cmp.HitBox)
    hitbox.centerx = player_hitbox.centerx + int((player_hitbox.w + front_range) * direction.value.x) / 2
    hitbox.centery = player_hitbox.centery + int((player_hitbox.h + front_range) * direction.value.y) / 2

    hitbox_entity_id = world.create_entity()
    world.add_component(hitbox_entity_id, hitbox)

    return hitbox_entity_id
