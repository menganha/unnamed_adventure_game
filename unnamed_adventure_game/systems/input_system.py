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
        velocity.x, velocity.y = 0, 0

        if self.keyboard.is_key_released(pygame.K_UP) or self.keyboard.is_key_released(pygame.K_DOWN):
            velocity.y = 0
            state.status = Status.IDLE
        if self.keyboard.is_key_down(pygame.K_DOWN):
            velocity.y = 1
            state.status = Status.MOVING
            state.direction = Direction.SOUTH
        if self.keyboard.is_key_down(pygame.K_UP):
            velocity.y = -1
            state.status = Status.MOVING
            state.direction = Direction.NORTH

        if self.keyboard.is_key_released(pygame.K_LEFT) or self.keyboard.is_key_released(pygame.K_RIGHT):
            self.world.component_for_entity(entity, cmp.Velocity).x = 0
            velocity.x = 0
            state.status = Status.IDLE
        if self.keyboard.is_key_down(pygame.K_LEFT):
            velocity.x = -1
            state.status = Status.MOVING
            state.direction = Direction.WEST
        if self.keyboard.is_key_down(pygame.K_RIGHT):
            velocity.x = 1
            state.status = Status.MOVING
            state.direction = Direction.EAST

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
