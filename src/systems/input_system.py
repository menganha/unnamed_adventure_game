import pygame

import config as CFG
import config as cfg
import esper
import event_manager
from components import Input, Velocity, Renderable, HitBox, Position, Weapon
from direction import Direction
from keyboard import Keyboard


class InputSystem(esper.Processor):

    def __init__(self):
        super().__init__()
        self.keyboard = Keyboard()

    def process(self):
        for ent, (inp) in self.world.get_component(Input):
            if inp.block_counter != 0:
                inp.block_counter -= 1
                return
            self.input_processing(ent, inp)

    def input_processing(self, entity: str, inp: Input):
        """
        Note: If moving in two directions at the same time, e.g., up and right, the renderable direction
        attribute will always be the one in the vertical direction, i.e, up
        """
        self.keyboard.process_input()

        if self.keyboard.is_key_released(pygame.K_UP) or self.keyboard.is_key_released(pygame.K_DOWN):
            self.world.component_for_entity(entity, Velocity).y = 0
        if self.keyboard.is_key_down(pygame.K_DOWN):
            self.world.component_for_entity(entity, Velocity).y = 1
            self.world.component_for_entity(entity, Renderable).direction = Direction.SOUTH
        if self.keyboard.is_key_down(pygame.K_UP):
            self.world.component_for_entity(entity, Velocity).y = -1
            self.world.component_for_entity(entity, Renderable).direction = Direction.NORTH

        if self.keyboard.is_key_released(pygame.K_LEFT) or self.keyboard.is_key_released(pygame.K_RIGHT):
            self.world.component_for_entity(entity, Velocity).x = 0
        if self.keyboard.is_key_down(pygame.K_LEFT):
            self.world.component_for_entity(entity, Velocity).x = -1
            self.world.component_for_entity(entity, Renderable).direction = Direction.WEST
        if self.keyboard.is_key_down(pygame.K_RIGHT):
            self.world.component_for_entity(entity, Velocity).x = +1
            self.world.component_for_entity(entity, Renderable).direction = Direction.EAST

        if self.keyboard.is_key_pressed(pygame.K_SPACE):
            # Stop player when is attacking
            self.world.component_for_entity(entity, Velocity).x = 0
            self.world.component_for_entity(entity, Velocity).y = 0

            # Creates a temporary hitbox representing the sword weapon
            player_sprite = self.world.component_for_entity(entity, Renderable)
            player_hb = self.world.component_for_entity(entity, HitBox)

            weapon = Weapon(damage=cfg.SWORD_DAMAGE, active_frames=cfg.SWORD_ACTIVE_FRAMES)
            if player_sprite.direction in (Direction.WEST, Direction.EAST):
                hitbox = HitBox(0, 0, cfg.SWORD_FRONT_RANGE, cfg.SWORD_SIDE_RANGE)
            else:
                hitbox = HitBox(0, 0, cfg.SWORD_SIDE_RANGE, cfg.SWORD_FRONT_RANGE)
            hitbox.rect.centerx = player_hb.rect.centerx + int((player_hb.rect.w + cfg.SWORD_FRONT_RANGE)
                                                               * player_sprite.direction.value.x) / 2
            hitbox.rect.centery = player_hb.rect.centery + int((player_hb.rect.h + cfg.SWORD_FRONT_RANGE)
                                                               * player_sprite.direction.value.y) / 2
            position = Position(hitbox.rect.x, hitbox.rect.y)
            self.world.create_entity(position, hitbox, weapon)

            # Block input until weapon life time is over and publish attach event
            inp.block_counter = weapon.active_frames
            event_manager.post_event('attack')

        if self.keyboard.is_key_pressed(pygame.K_q):
            CFG.DEBUG_MODE = not CFG.DEBUG_MODE
