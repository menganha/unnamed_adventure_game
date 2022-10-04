"""
The module gathers functions that add commonly used entities to an input world
"""

from copy import copy

from yazelc import components as cmp
from yazelc import config as cfg
from yazelc import visual_effects as vfx
from yazelc import zesper
from yazelc.controller import Button
from yazelc.event import PauseEvent
from yazelc.systems.input_system import InputMessage
from yazelc.utils.game_utils import Direction, Status

VELOCITY = 1.5 - 1e-8  # This ensures that the rounding produces the displacement pattern 1,2,1,2... that averages a velocity of 1.5
VELOCITY_DIAGONAL = 1

HITBOX_HEIGHT = 9
HITBOX_WIDTH = 10
SPRITE_SIZE = 32
SPRITE_DEPTH = 200

MAX_HEALTH = 10  # Should always be divisible by two

ATTACK_ANIMATION_FRAMES = 5
IDLE_ANIMATION_FRAME = 10

# TODO: Modify the sprite such that the range of the sword is the same on all cardinal directions!!!
SWORD_FRONT_RANGE = 15
SWORD_SIDE_RANGE = 20
SWORD_DAMAGE = 5
SWORD_ACTIVE_FRAMES = ATTACK_ANIMATION_FRAMES * 4
SWORD_RECOIL_VEL = 5
SWORD_SPRITE_WIDTH = 48

BOMB_SPRITES_ID = 'BOMB'
BOMB_DAMAGE = 3
BOMB_SPRITE_WIDTH = 16

INTERACTIVE_FRONT_RANGE = 10
INTERACTIVE_SIDE_RANGE = 2


def create_player_at(center_x_pos: int, center_y_pos: int, world: zesper.World) -> int:
    """ Creates the player entity centered at the given position"""

    player_entity_id = world.create_entity()
    stripe = world.resource_manager.get_animation_strip(f'{Status.IDLE.name}_{Direction.DOWN.name}')
    world.add_component(player_entity_id, cmp.Renderable(stripe[0], depth=SPRITE_DEPTH))
    world.add_component(player_entity_id, cmp.Animation(stripe, delay=IDLE_ANIMATION_FRAME))

    # HitBox
    hitbox_component = cmp.HitBox(0, 0, HITBOX_WIDTH, HITBOX_HEIGHT)
    hitbox_component.rect.center = (center_x_pos, center_y_pos)
    world.add_component(player_entity_id, hitbox_component)

    # Other components
    x_pos, y_pos = get_position_of_sprite(hitbox_component)
    world.add_component(player_entity_id, cmp.Position(x=x_pos, y=y_pos))
    world.add_component(player_entity_id, cmp.Velocity(x=0, y=0))
    world.add_component(player_entity_id, cmp.Input(handle_input_function=handle_input))
    world.add_component(player_entity_id, cmp.State(Status.IDLE, Direction.DOWN))
    world.add_component(player_entity_id, cmp.Health(points=MAX_HEALTH))
    return player_entity_id


def get_position_of_sprite(hitbox: cmp.HitBox):
    """ Gets the position of the sprite from the player's Hitbox """
    relative_pos_x = SPRITE_SIZE // 2
    relative_pos_y = SPRITE_SIZE // 2 + 3
    return hitbox.rect.centerx - relative_pos_x, hitbox.rect.centery - relative_pos_y


def create_bomb(player_entity_id: int, world: zesper.World):
    bomb_explosion_delay_time = 100
    bomb_entity = world.create_entity()
    strip = world.resource_manager.get_animation_strip(BOMB_SPRITES_ID)

    position = world.component_for_entity(player_entity_id, cmp.Position)
    direction = world.component_for_entity(player_entity_id, cmp.State).direction
    renderable = world.component_for_entity(player_entity_id, cmp.Renderable)

    bomb_renderable_component = cmp.Renderable(image=strip[0])

    bomb_position_center_x = position.x + renderable.width // 2 + direction.value.x * 8
    bomb_position_center_y = position.y + renderable.height // 2 + direction.value.y * 8
    bomb_position_x = bomb_position_center_x - bomb_renderable_component.width // 2
    bomb_position_y = bomb_position_center_y - bomb_renderable_component.height // 2

    script_arguments = {'bomb_entity_id': bomb_entity, 'x_pos': bomb_position_center_x, 'y_pos': bomb_position_center_y, 'world': world}

    world.add_component(bomb_entity, bomb_renderable_component)
    frame_sequence = [0] * 52 + [0, 0, 1, 1, 2, 2] * 8
    world.add_component(bomb_entity, cmp.Animation(strip, 0, frame_sequence))
    world.add_component(bomb_entity, cmp.Position(bomb_position_x, bomb_position_y))
    world.add_component(bomb_entity, cmp.Timer(delay=bomb_explosion_delay_time, callback=create_bomb_hitbox, **script_arguments))


def create_bomb_hitbox(bomb_entity_id: int, x_pos: int, y_pos: int, world: zesper.World):
    bomb_range = 20
    hitbox = cmp.HitBox(0, 0, bomb_range * 2, bomb_range * 2)
    hitbox.rect.center = x_pos, y_pos
    world.add_component(bomb_entity_id, hitbox)
    world.add_component(bomb_entity_id, cmp.Weapon(damage=BOMB_DAMAGE, active_frames=10))
    vfx.create_explosion(hitbox.rect.centerx, hitbox.rect.centery, 60, bomb_range, cfg.C_RED, world)


def create_melee_weapon(player_entity_id: int, world: zesper.World):
    """ Creates a Weapon hitbox for the parent entity with a hitbox """
    weapon_entity_id = _create_hitbox_in_front(player_entity_id, SWORD_FRONT_RANGE, SWORD_SIDE_RANGE, world)
    world.add_component(weapon_entity_id,
                        cmp.Weapon(damage=SWORD_DAMAGE, active_frames=SWORD_ACTIVE_FRAMES, freeze_frames=8,
                                   recoil_velocity=SWORD_RECOIL_VEL))

    direction = world.component_for_entity(player_entity_id, cmp.State).direction
    strip = world.resource_manager.get_animation_strip(f'wooden_sword_{direction.name}')
    world.add_component(weapon_entity_id, cmp.Animation(strip, ATTACK_ANIMATION_FRAMES, one_loop=True))
    world.add_component(weapon_entity_id, cmp.Renderable(strip[0], SPRITE_DEPTH + 1))
    position = copy(world.component_for_entity(player_entity_id, cmp.Position))
    position.x = position.x - (SWORD_SPRITE_WIDTH - SPRITE_SIZE) // 2
    position.y = position.y - (SWORD_SPRITE_WIDTH - SPRITE_SIZE) // 2
    world.add_component(weapon_entity_id, position)


def create_interactive_hitbox(player_entity_id: int, world: zesper.World):
    """ Creates a hitbox to detect interaction with other objects """
    entity_id = _create_hitbox_in_front(player_entity_id, INTERACTIVE_FRONT_RANGE, INTERACTIVE_SIDE_RANGE, world)
    world.add_component(entity_id, cmp.InteractorTag())
    frames_until_destroyed = 0
    world.add_component(entity_id, cmp.Timer(frames_until_destroyed, world.delete_entity, entity=entity_id))


def handle_input(input_message: InputMessage):
    # TODO: Add state system just for this operation. It decouples the input and is mostly useful
    #       if we want to  remove this process but don't want to stop the state update

    if input_message.controller.is_button_pressed(Button.START):
        input_message.event_list.append(PauseEvent())
        return

    else:
        velocity = input_message.world.component_for_entity(input_message.ent_id, cmp.Velocity)
        position = input_message.world.component_for_entity(input_message.ent_id, cmp.Position)

        direction_x = - input_message.controller.is_button_down(Button.LEFT) + input_message.controller.is_button_down(Button.RIGHT)
        direction_y = - input_message.controller.is_button_down(Button.UP) + input_message.controller.is_button_down(Button.DOWN)

        abs_vel = VELOCITY_DIAGONAL if (direction_y and direction_x) else VELOCITY
        velocity.x = direction_x * abs_vel
        velocity.y = direction_y * abs_vel

        # Snaps position to grid when the respective key has been released.  This allows for a deterministic movement
        # pattern by eliminating any decimal residual accumulated when resetting the position to an integer value
        horizontal_key_released = (input_message.controller.is_button_released(Button.LEFT) or
                                   input_message.controller.is_button_released(Button.RIGHT))
        vertical_key_released = (input_message.controller.is_button_released(Button.UP) or
                                 input_message.controller.is_button_released(Button.DOWN))

        if horizontal_key_released:
            position.x = round(position.x)
        if vertical_key_released:
            position.y = round(position.y)

        # Attempt to change direction only when a key is released or the status of the entity is not moving
        state = input_message.world.component_for_entity(input_message.ent_id, cmp.State)
        if horizontal_key_released or vertical_key_released or state.status != Status.MOVING:
            if direction_x > 0:
                state.direction = Direction.RIGHT
            elif direction_x < 0:
                state.direction = Direction.LEFT
            if direction_y > 0:
                state.direction = Direction.DOWN
            elif direction_y < 0:
                state.direction = Direction.UP

        # Set entity status for animation system
        if not direction_x and not direction_y:
            state.status = Status.IDLE
        else:
            state.status = Status.MOVING

        # Change animation
        if state.has_changed():
            animation_identifier = f'{state.status.name}_{state.direction.name}'
            strip = input_message.world.resource_manager.get_animation_strip(animation_identifier)
            input_message.world.add_component(input_message.ent_id, cmp.Animation(strip, IDLE_ANIMATION_FRAME))
        state.refresh()

        if input_message.controller.is_button_pressed(Button.B):  # Stop player when is attacking
            velocity.x = 0
            velocity.y = 0
            state.status = Status.ATTACKING
            state.refresh()

            animation_identifier = f'{state.status.name}_{state.direction.name}'
            strip = input_message.world.resource_manager.get_animation_strip(animation_identifier)
            input_message.world.add_component(input_message.ent_id, cmp.Animation(strip, ATTACK_ANIMATION_FRAMES))

            # Creates a temporary hitbox representing the sword weapon
            create_melee_weapon(input_message.ent_id, input_message.world)

            # Block input until weapon lifetime is over and publish attach event. We need to block it one less than
            # The active frames as we are counting already the frame when it is activated as active
            input_ = input_message.world.component_for_entity(input_message.ent_id, cmp.Input)
            input_.block_counter = SWORD_ACTIVE_FRAMES - 1

        if input_message.controller.is_button_pressed(Button.A):
            create_interactive_hitbox(input_message.ent_id, input_message.world)

        if input_message.controller.is_button_pressed(Button.L):
            vfx.create_explosion(position.x, position.y, 30, 30, cfg.C_WHITE, input_message.world)

        if input_message.controller.is_button_pressed(Button.X):
            create_bomb(input_message.ent_id, input_message.world)

        if input_message.controller.is_button_pressed(Button.SELECT):
            cfg.DEBUG_MODE = not cfg.DEBUG_MODE


def _create_hitbox_in_front(player_entity_id: int, front_range: int, side_range: int, world: zesper.World) -> int:
    """ Creates a hitbox in the direction the player is facing """
    direction = world.component_for_entity(player_entity_id, cmp.State).direction
    if direction in (Direction.LEFT, Direction.RIGHT):
        hitbox = cmp.HitBox(0, 0, front_range, side_range)
    else:
        hitbox = cmp.HitBox(0, 0, side_range, front_range)

    player_hitbox = world.component_for_entity(player_entity_id, cmp.HitBox)
    hitbox.rect.centerx = player_hitbox.rect.centerx + int((player_hitbox.rect.w + front_range) * direction.value.x) / 2
    hitbox.rect.centery = player_hitbox.rect.centery + int((player_hitbox.rect.h + front_range) * direction.value.y) / 2

    hitbox_entity_id = world.create_entity()
    world.add_component(hitbox_entity_id, hitbox)

    return hitbox_entity_id
