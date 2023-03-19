from pathlib import Path

import pygame

from yazelc import config as cfg
from yazelc.components import Renderable, Position
from yazelc.cutscene.fade_task import FadeInTask, FadeOutTask
from yazelc.cutscene.move_task import MoveTask
from yazelc.cutscene.spawn_task import SpawnTask
from yazelc.cutscene.wait_task import WaitTask
from yazelc.scenes.base_scene import BaseScene
from yazelc.systems.cutscene_system import CutsceneSystem
from yazelc.systems.movement_system import MovementSystem
from yazelc.systems.render_system import RenderSystem
from yazelc.tween import TweenFunction
from yazelc.utils.game_utils import IVec

ASSET_PATH = Path('assets', 'sprites')
PG_LOGO = ASSET_PATH / 'pygame_powered_logo.png'
SHIELD_LOGO = ASSET_PATH / 'shield_logo.png'
MUSIC_PATH = Path('assets', 'music', 'Quantic_Flowering_Inferno-Cumbia_Sobre_el_Mar.ogg')

FONT_PATH = Path('assets', 'font', 'Anonymous Pro.ttf')
FONT_COLOR = cfg.C_WHITE
FONT_SIZE = 11
TITLE_TEXT = 'A game by\nClimacus'


class IntroScene(BaseScene):

    def on_enter(self):
        # load resources
        pg_logo_surface = self.world.resource_manager.add_texture(PG_LOGO)
        pg_logo_surface.set_alpha(0)
        scale = 0.10
        pg_logo_surface = pygame.transform.smoothscale(pg_logo_surface,
                                                       (int(pg_logo_surface.get_width() * scale),
                                                        int(pg_logo_surface.get_height() * scale)))
        shield_surface = self.world.resource_manager.add_texture(SHIELD_LOGO)
        pygame.mixer.music.load(MUSIC_PATH)
        pygame.mixer.music.play(-1)

        font = self.world.resource_manager.add_font(FONT_PATH, FONT_SIZE, FONT_COLOR, 'font')

        # Alternative source
        text_surface_alt = font.render(TITLE_TEXT, center=True)

        # Entities
        center = IVec((cfg.RESOLUTION.x - pg_logo_surface.get_width()) // 2, (cfg.RESOLUTION.y - pg_logo_surface.get_height()) // 2)
        pg_logo_ent = self.world.create_entity(Position.from_ivec(center, True), Renderable(pg_logo_surface))

        shield_ent = self.world.create_entity(Position(0, -150, absolute=True), Renderable(shield_surface))
        text_ent_components = (Position(30, 30, absolute=True), Renderable(text_surface_alt))

        # Set cutscene
        task_list = [
            FadeInTask(pg_logo_ent, TweenFunction.EASE_OUT_CUBIC, duration_frames=300),
            WaitTask(duration_frames=100),
            FadeOutTask(pg_logo_ent, TweenFunction.EASE_OUT_CUBIC, duration_frames=150),
            WaitTask(duration_frames=80),
            SpawnTask(*text_ent_components, duration_frames=150),
            WaitTask(duration_frames=200),
            MoveTask(shield_ent, final_pos=IVec(0, 90), duration_frames=300),
        ]

        # Set systems
        render_sys = RenderSystem(self.window)
        cutscene_sys = CutsceneSystem(*task_list)
        self.world.add_processor(render_sys)
        self.world.add_processor(cutscene_sys)
        self.world.add_processor(MovementSystem())

    def on_exit(self):
        pass
