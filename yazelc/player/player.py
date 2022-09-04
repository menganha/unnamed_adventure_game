"""
The module gathers functions that add commonly used entities to an input world
"""
from pathlib import Path

from yazelc import components as cmp
from yazelc import config as cfg
from yazelc import event_manager
from yazelc import visual_effects as vfx
from yazelc import zesper
from yazelc.animation import AnimationStrip
from yazelc.controller import Controller, Button
from yazelc.event_type import EventType
from yazelc.items import ItemType
from yazelc.menu import menu_box
from yazelc.utils.game_utils import Direction, Status

VELOCITY = 1.5 - 1e-8  # This ensures that the rounding produces the displacement pattern 1,2,1,2... that averages a velocity of 1.5
VELOCITY_DIAGONAL = 1

HITBOX_HEIGHT = 14
HITBOX_WIDTH = 14
SPRITE_SIZE = 32
SPRITE_DEPTH = 200

MAX_HEALTH = 10  # Should always be divisible by two

INVENTORY = {item_type: 0 for item_type in ItemType if item_type != ItemType.HEART}

# TODO: Modify the sprite such that the range of the sword is the same on all cardinal directions!!!
SWORD_FRONT_RANGE = 5
SWORD_SIDE_RANGE = 20
SWORD_DAMAGE = 5
SWORD_ACTIVE_FRAMES = 12

BOMB_DAMAGE = 3

INTERACTIVE_FRONT_RANGE = 10
INTERACTIVE_SIDE_RANGE = 2


def create_player_at(center_x_pos: int, center_y_pos: int, world: zesper.World):
    """ Creates the player entity centered at the given position"""

    player_entity_id = world.create_entity()
    world.player_entity_id = player_entity_id

    # Create Animations dictionary and add it as a component
    kwargs = {}
    for typ in ['idle', 'move', 'attack']:
        for direction in ['up', 'down', 'right']:
            img_path = Path('assets', 'sprites', 'player', f'{typ}_{direction}.png')
            delay = 4 if typ == 'attack' else 7
            kwargs.update({f'{typ}_{direction}': AnimationStrip(img_path, sprite_width=SPRITE_SIZE, delay=delay)})

    world.add_component(player_entity_id, cmp.Renderable(image=kwargs['idle_down'][0], depth=SPRITE_DEPTH))
    world.add_component(player_entity_id, cmp.Animation(**kwargs))

    # HitBox
    hitbox_component = cmp.HitBox(0, 0, HITBOX_WIDTH, HITBOX_HEIGHT)
    hitbox_component.rect.center = (center_x_pos, center_y_pos)
    world.add_component(player_entity_id, hitbox_component)

    # Other components
    x_pos, y_pos = get_position_of_sprite(hitbox_component)
    world.add_component(player_entity_id, cmp.Position(x=x_pos, y=y_pos))
    world.add_component(player_entity_id, cmp.Velocity(x=0, y=0))
    world.add_component(player_entity_id, cmp.Input(handle_input_function=handle_input))
    world.add_component(player_entity_id, cmp.Health(points=MAX_HEALTH))


def get_position_of_sprite(hitbox: cmp.HitBox):
    """ Gets the position of the sprite from the player's Hitbox """
    relative_pos_x = SPRITE_SIZE // 2
    relative_pos_y = SPRITE_SIZE // 2
    return hitbox.rect.centerx - relative_pos_x, hitbox.rect.centery - relative_pos_y


def create_bomb(player_entity_id: int, world: zesper.World):
    bomb_entity = world.create_entity()
    img_path = Path('assets', 'sprites', 'bomb.png')  # TODO: Add to resource manager and animation strip gets from resources as well
    frame_sequence = [0] * 52 + [0, 0, 1, 1, 2, 2] * 8
    animation_stripe = AnimationStrip(img_path, sprite_width=16, frame_sequence=frame_sequence)

    position = world.component_for_entity(player_entity_id, cmp.Position)
    direction = world.component_for_entity(player_entity_id, cmp.Animation).direction
    renderable = world.component_for_entity(player_entity_id, cmp.Renderable)

    bomb_renderable_component = cmp.Renderable(image=animation_stripe[0])

    bomb_position_center_x = position.x + renderable.width // 2 + direction.value.x * 8
    bomb_position_center_y = position.y + renderable.height // 2 + direction.value.y * 8
    bomb_position_x = bomb_position_center_x - bomb_renderable_component.width // 2
    bomb_position_y = bomb_position_center_y - bomb_renderable_component.height // 2

    script_arguments = (bomb_entity, bomb_position_center_x, bomb_position_center_y)

    world.add_component(bomb_entity, bomb_renderable_component)
    world.add_component(bomb_entity, cmp.Animation(idle_down=animation_stripe))
    world.add_component(bomb_entity, cmp.Position(bomb_position_x, bomb_position_y))
    world.add_component(bomb_entity, cmp.Script(delay=100, function=create_bomb_hitbox, args=script_arguments))


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
    world.add_component(weapon_entity_id, cmp.Weapon(damage=SWORD_DAMAGE, active_frames=SWORD_ACTIVE_FRAMES))


def create_interactive_hitbox(player_entity_id: int, world: zesper.World):
    """ Creates a hitbox to detect interaction with other objects """
    entity_id = _create_hitbox_in_front(player_entity_id, INTERACTIVE_FRONT_RANGE, INTERACTIVE_SIDE_RANGE, world)

    def remove_entity(ent: int, world_: zesper.World):
        world_.delete_entity(ent)

    world.add_component(entity_id, cmp.InteractorTag())
    world.add_component(entity_id, cmp.Script(remove_entity, args=(entity_id,), delay=0))


def handle_input(player_entity: int, controller: Controller, world: zesper.World):
    # TODO: Add state system just for this operation. It decouples the input and is mostly useful if we want to
    #   remove this process but don't want to stop the state update
    animation = world.component_for_entity(player_entity, cmp.Animation)
    animation.previous_status = animation.status
    animation.previous_direction = animation.direction

    if controller.is_button_pressed(Button.START):
        menu_box.create_pause_menu(world)
        event_manager.post_event(EventType.PAUSE)
        return

    input_ = world.component_for_entity(player_entity, cmp.Input)
    if input_.block_counter != 0:
        input_.block_counter -= 1

    else:
        velocity = world.component_for_entity(player_entity, cmp.Velocity)
        position = world.component_for_entity(player_entity, cmp.Position)

        direction_x = - controller.is_button_down(Button.LEFT) + controller.is_button_down(Button.RIGHT)
        direction_y = - controller.is_button_down(Button.UP) + controller.is_button_down(Button.DOWN)

        abs_vel = VELOCITY_DIAGONAL if (direction_y and direction_x) else VELOCITY
        velocity.x = direction_x * abs_vel
        velocity.y = direction_y * abs_vel

        # Snaps position to grid when the respective key has been released.  This allows for a deterministic movement
        # pattern by eliminating any decimal residual accumulated when resetting the position to an integer value
        horizontal_key_released = controller.is_button_released(Button.LEFT) or controller.is_button_released(Button.RIGHT)
        vertical_key_released = controller.is_button_released(Button.UP) or controller.is_button_released(Button.DOWN)

        if horizontal_key_released:
            position.x = round(position.x)
        if vertical_key_released:
            position.y = round(position.y)

        # Attempt to change direction only when a key is released or the status of the entity is not moving
        if horizontal_key_released or vertical_key_released or animation.status != Status.MOVING:
            if direction_x > 0:
                animation.direction = Direction.EAST
            elif direction_x < 0:
                animation.direction = Direction.WEST
            if direction_y > 0:
                animation.direction = Direction.SOUTH
            elif direction_y < 0:
                animation.direction = Direction.NORTH

        # Set entity status for animation system
        if not direction_x and not direction_y:
            animation.status = Status.IDLE
        else:
            animation.status = Status.MOVING

        if controller.is_button_pressed(Button.B):
            # Stop player when is attacking
            velocity.x = 0
            velocity.y = 0
            animation.status = Status.ATTACKING

            # Creates a temporary hitbox representing the sword weapon
            create_melee_weapon(player_entity, world)

            # Block input until weapon lifetime is over and publish attach event. We need to block it one less than
            # The active frames as we are counting already the frame when it is activated as active
            input_.block_counter = SWORD_ACTIVE_FRAMES - 1

        if controller.is_button_pressed(Button.A):
            create_interactive_hitbox(player_entity, world)

        if controller.is_button_pressed(Button.L):
            vfx.create_explosion(position.x, position.y, 30, 30, cfg.C_WHITE, world)

        if controller.is_button_pressed(Button.X):
            create_bomb(player_entity, world)

        if controller.is_button_pressed(Button.SELECT):
            cfg.DEBUG_MODE = not cfg.DEBUG_MODE


def _create_hitbox_in_front(player_entity_id: int, front_range: int, side_range: int, world: zesper.World) -> int:
    """ Creates a hitbox in the direction the player is facing """
    direction = world.component_for_entity(player_entity_id, cmp.Animation).direction
    if direction in (Direction.WEST, Direction.EAST):
        hitbox = cmp.HitBox(0, 0, front_range, side_range)
    else:
        hitbox = cmp.HitBox(0, 0, side_range, front_range)

    player_hitbox = world.component_for_entity(player_entity_id, cmp.HitBox)
    hitbox.rect.centerx = player_hitbox.rect.centerx + int((player_hitbox.rect.w + front_range) * direction.value.x) / 2
    hitbox.rect.centery = player_hitbox.rect.centery + int((player_hitbox.rect.h + front_range) * direction.value.y) / 2

    hitbox_entity_id = world.create_entity()
    world.add_component(hitbox_entity_id, hitbox)
    world.add_component(hitbox_entity_id, cmp.Position(hitbox.rect.x, hitbox.rect.y))

    return hitbox_entity_id
