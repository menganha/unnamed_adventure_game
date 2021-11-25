import esper

import yazelc.components as cmp
from yazelc import event_manager
from yazelc.event_type import EventType
from yazelc.keyboard import Keyboard
from yazelc.systems.animation_system import AnimationSystem
from yazelc.systems.collision_system import CollisionSystem
from yazelc.systems.combat_system import CombatSystem
from yazelc.systems.menu_system import MenuSystem
from yazelc.systems.movement_system import MovementSystem
from yazelc.systems.script_system import ScriptSystem
from yazelc.systems.transition_system import TransitionSystem
from yazelc.systems.visual_effects_system import VisualEffectsSystem


class InputSystem(esper.Processor):
    PROCESSOR_TYPES = [MovementSystem, ScriptSystem, CollisionSystem, CombatSystem, VisualEffectsSystem, TransitionSystem, AnimationSystem]

    def __init__(self):
        super().__init__()
        self.keyboard = Keyboard()
        self.paused = False
        self.processors = None
        event_manager.subscribe(EventType.PAUSE, self.on_pause)

    def process(self):
        # Initialized here as cannot have all system references when instantiated.
        # TODO: Consider having this list as a global?
        if not self.processors:
            self.processors = [self.world.get_processor(proc) for proc in self.PROCESSOR_TYPES]

        self.keyboard.process_input()

        for entity, (input_, state) in self.world.get_components(cmp.Input, cmp.State):
            state.previous_status = state.status
            state.previous_direction = state.direction
            if input_.block_counter != 0:
                input_.block_counter -= 1
                return
            input_.handle_input_function(entity, input_, self.keyboard, self.world)

    def on_pause(self):
        self.paused = not self.paused

        if self.paused:
            for proc in self.PROCESSOR_TYPES:
                self.world.remove_processor(proc)
            pause_menu = self.world.get_processor(MenuSystem).pause_menu
            pause_menu.create_entity(self.world)
        else:
            for proc in self.processors:
                self.world.add_processor(proc)
            pause_menu = self.world.get_processor(MenuSystem).pause_menu
            pause_menu.delete_entity(self.world)
