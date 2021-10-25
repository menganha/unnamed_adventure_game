import pygame

import config as CFG
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
            """ Creates a temporary hitbox representing the weapon """
            player_sprite = self.world.component_for_entity(entity, Renderable)
            player_hb = self.world.component_for_entity(entity, HitBox)
            weapon = Weapon(range_front=5, range_side=20, offset=player_hb.rect.w, life_time=20)
            if player_sprite.direction in (Direction.WEST, Direction.EAST):
                hitbox = HitBox(0, 0, weapon.range_front, weapon.range_side)
            else:
                hitbox = HitBox(0, 0, weapon.range_side, weapon.range_front)
            hitbox.rect.centerx = player_hb.rect.centerx + \
                                  int((weapon.offset + weapon.range_front) * player_sprite.direction.value.x) / 2
            hitbox.rect.centery = player_hb.rect.centery + \
                                  int((weapon.offset + weapon.range_front) * player_sprite.direction.value.y) / 2
            position = Position(hitbox.rect.x, hitbox.rect.y)
            self.world.create_entity(position, hitbox, weapon)
            inp.block_counter = weapon.life_time
            self.world.component_for_entity(entity, Velocity).x = 0
            self.world.component_for_entity(entity, Velocity).y = 0
            event_manager.post_event('attack')

        if self.keyboard.is_key_pressed(pygame.K_q):
            CFG.DEBUG_MODE = not CFG.DEBUG_MODE
