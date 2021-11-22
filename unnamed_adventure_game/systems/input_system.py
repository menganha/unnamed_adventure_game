import esper
import pygame

import unnamed_adventure_game.components as cmp
import unnamed_adventure_game.config as cfg
import unnamed_adventure_game.visual_effects as vfx
from unnamed_adventure_game.entity_fabric import create_melee_weapon, create_bomb_at
from unnamed_adventure_game.keyboard import Keyboard
from unnamed_adventure_game.utils.game import Direction, Status


class InputSystem(esper.Processor):

    def __init__(self):
        super().__init__()
        self.keyboard = Keyboard()

    def process(self):
        for entity, (input_) in self.world.get_component(cmp.Input):
            state = self.world.component_for_entity(entity, cmp.State)  # TODO: code smell: should we introduce a standalone state system?
            state.previous_status = state.status
            state.previous_direction = state.direction
            if input_.block_counter != 0:
                input_.block_counter -= 1
                return
            self.input_processing(entity, input_)

    def input_processing(self, entity: int, input_: cmp.Input):
        """
        Note: If moving in two directions at the same time, e.g., up and right, the renderable direction
        attribute will always be the one in the vertical direction, i.e, up
        """
        self.keyboard.process_input()

        state = self.world.component_for_entity(entity, cmp.State)
        velocity = self.world.component_for_entity(entity, cmp.Velocity)
        position = self.world.component_for_entity(entity, cmp.Position)

        direction_x = - self.keyboard.is_key_down(pygame.K_LEFT) + self.keyboard.is_key_down(pygame.K_RIGHT)
        direction_y = - self.keyboard.is_key_down(pygame.K_UP) + self.keyboard.is_key_down(pygame.K_DOWN)

        abs_vel = cfg.VELOCITY_DIAGONAL if (direction_y and direction_x) else cfg.VELOCITY
        velocity.x = direction_x * abs_vel
        velocity.y = direction_y * abs_vel

        # Snaps position to grid when the respective key has been released.  This allows for a deterministic movement
        # pattern by eliminating any decimal residual accumulated when resetting the position to a integer value
        horizontal_key_released = self.keyboard.is_key_released(pygame.K_LEFT) or self.keyboard.is_key_released(pygame.K_RIGHT)
        vertical_key_released = self.keyboard.is_key_released(pygame.K_UP) or self.keyboard.is_key_released(pygame.K_DOWN)

        if horizontal_key_released:
            position.x = round(position.x)
        if vertical_key_released:
            position.y = round(position.y)

        # Attempt to change direction only when a key is released or the status of the entity is not moving
        if horizontal_key_released or vertical_key_released or state.status != Status.MOVING:
            if direction_x > 0:
                state.direction = Direction.EAST
            elif direction_x < 0:
                state.direction = Direction.WEST
            if direction_y > 0:
                state.direction = Direction.SOUTH
            elif direction_y < 0:
                state.direction = Direction.NORTH

        # Set entity status for animation system
        if not direction_x and not direction_y:
            state.status = Status.IDLE
        else:
            state.status = Status.MOVING

        if self.keyboard.is_key_pressed(pygame.K_SPACE):
            # Stop player when is attacking
            velocity = self.world.component_for_entity(entity, cmp.Velocity)
            velocity.x = 0
            velocity.y = 0
            state.status = Status.ATTACKING

            # Creates a temporary hitbox representing the sword weapon
            hitbox = self.world.component_for_entity(entity, cmp.HitBox)
            create_melee_weapon(hitbox, state.direction, cfg.SWORD_FRONT_RANGE, cfg.SWORD_SIDE_RANGE,
                                cfg.SWORD_DAMAGE, cfg.SWORD_ACTIVE_FRAMES, self.world)

            # Block input until weapon life time is over and publish attach event. We need to block it one less than
            # The active frames as we are counting already the frame when it is activated as active
            input_.block_counter = cfg.SWORD_ACTIVE_FRAMES - 1

        if self.keyboard.is_key_pressed(pygame.K_e):
            vfx.create_explosion(position.x, position.y, 30, 30, cfg.C_WHITE, self.world)

        if self.keyboard.is_key_pressed(pygame.K_b):
            create_bomb_at(entity, self.world)

        if self.keyboard.is_key_pressed(pygame.K_q):
            cfg.DEBUG_MODE = not cfg.DEBUG_MODE
