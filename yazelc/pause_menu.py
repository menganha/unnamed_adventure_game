import esper
import pygame

import yazelc.components as cmp
import yazelc.config as cfg
import yazelc.text as text
from yazelc import event_manager
from yazelc.event_type import EventType
from yazelc.keyboard import Keyboard
from yazelc.systems.camera_system import CameraSystem


class PauseMenu:
    WIDTH = 150
    HEIGHT = 50
    BG_COLOR = cfg.C_BLACK
    FG_COLOR = cfg.C_WHITE
    ALPHA = 180

    def __init__(self):
        self.background = pygame.Surface((self.WIDTH, self.HEIGHT))
        self.entity = None

        self.background.fill(self.BG_COLOR)
        self.background.set_alpha(self.ALPHA)

        pause_text = text.Text('PAUSE', size=8, color=self.FG_COLOR)
        continue_text = text.Text('Continue', size=8, color=self.FG_COLOR)
        quit_text = text.Text('Quit', size=8, color=self.FG_COLOR)

        pause_text.render_at(self.background, pos_y=3)
        continue_text.render_at(self.background, pos_y=20)
        quit_text.render_at(self.background, pos_y=30)

    def create_entity(self, world: esper.World):
        camera_entity = world.get_processor(CameraSystem).camera_entity
        camera_pos = world.component_for_entity(camera_entity, cmp.Position)

        menu_pos_x = round(-camera_pos.x + (cfg.RESOLUTION[0] - self.WIDTH) // 2)
        menu_pos_y = round(-camera_pos.y + (cfg.RESOLUTION[1] - self.HEIGHT) // 2)

        self.entity = world.create_entity()
        world.add_component(self.entity, cmp.Renderable(image=self.background))
        world.add_component(self.entity, cmp.Position(menu_pos_x, menu_pos_y))
        world.add_component(self.entity, cmp.Menu(0, 0, 2, 0))
        world.add_component(self.entity, cmp.Input(handle_input_function=PauseMenu.handle_menu_input))

    def delete_entity(self, world: esper.World):
        world.delete_entity(self.entity)
        self.entity = None

    @staticmethod
    def handle_menu_input(entity: int, input_: cmp.Input, keyboard: Keyboard, world: esper.World):
        direction_x = - keyboard.is_key_down(pygame.K_LEFT) + keyboard.is_key_down(pygame.K_RIGHT)
        direction_y = - keyboard.is_key_down(pygame.K_UP) + keyboard.is_key_down(pygame.K_DOWN)

        if keyboard.is_key_pressed(pygame.K_p):
            event_manager.post_event(EventType.PAUSE)
