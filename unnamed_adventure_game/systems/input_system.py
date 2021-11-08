import esper
import pygame

import unnamed_adventure_game.components as cmp
import unnamed_adventure_game.config as cfg
from unnamed_adventure_game.entity_fabric import create_melee_weapon
from unnamed_adventure_game.keyboard import Keyboard
from unnamed_adventure_game.utils.game import Direction, Status


class InputSystem(esper.Processor):

    def __init__(self):
        super().__init__()
        self.keyboard = Keyboard()

    def process(self):
        for ent, (input_) in self.world.get_component(cmp.Input):
            if input_.block_counter != 0:
                input_.block_counter -= 1
                return
            self.input_processing(ent, input_)

    def input_processing(self, entity: str, input_: cmp.Input):
        """
        Note: If moving in two directions at the same time, e.g., up and right, the renderable direction
        attribute will always be the one in the vertical direction, i.e, up
        """
        self.keyboard.process_input()

        state = self.world.component_for_entity(entity, cmp.State)
        velocity = self.world.component_for_entity(entity, cmp.Velocity)
        position = self.world.component_for_entity(entity, cmp.Position)

        # Snaps position to grid when the respective key has been released.
        # This allows for a deterministic movement pattern by eliminating any decimal residual accumulated and resetting
        # the position to a integer value
        if self.keyboard.is_key_released(pygame.K_LEFT) or self.keyboard.is_key_released(pygame.K_RIGHT):
            position.x = round(position.x)
        if self.keyboard.is_key_released(pygame.K_UP) or self.keyboard.is_key_released(pygame.K_DOWN):
            position.y = round(position.y)

        direction_x = - self.keyboard.is_key_down(pygame.K_LEFT) + self.keyboard.is_key_down(pygame.K_RIGHT)
        direction_y = - self.keyboard.is_key_down(pygame.K_UP) + self.keyboard.is_key_down(pygame.K_DOWN)

        abs_vel = 1 if (direction_y and direction_x) else 1.5 - 1e-8  # TODO: set this variables to some config module
        velocity.x = direction_x * abs_vel
        velocity.y = direction_y * abs_vel

        if (self.keyboard.is_key_released(pygame.K_LEFT) or self.keyboard.is_key_released(pygame.K_RIGHT)
            or self.keyboard.is_key_released(pygame.K_UP) or self.keyboard.is_key_released(pygame.K_DOWN)) or state.status != Status.MOVING:
            if direction_x > 0:
                state.direction = Direction.EAST
            elif direction_x < 0:
                state.direction = Direction.WEST
            if direction_y > 0:
                state.direction = Direction.SOUTH
            elif direction_y < 0:
                state.direction = Direction.NORTH

        # Set entity status for animation system
        tmp = [direction_y, direction_x]
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

            # Block input until weapon life time is over and publish attach event
            input_.block_counter = cfg.SWORD_ACTIVE_FRAMES

        if self.keyboard.is_key_pressed(pygame.K_q):
            cfg.DEBUG_MODE = not cfg.DEBUG_MODE
