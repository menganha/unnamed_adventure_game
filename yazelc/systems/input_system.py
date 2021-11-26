import esper

from yazelc import components as cmp
from yazelc import event_manager
from yazelc import pause_menu
from yazelc.controller import Controller
from yazelc.event_type import EventType
from yazelc.systems.animation_system import AnimationSystem
from yazelc.systems.collision_system import CollisionSystem
from yazelc.systems.combat_system import CombatSystem
from yazelc.systems.movement_system import MovementSystem
from yazelc.systems.script_system import ScriptSystem
from yazelc.systems.transition_system import TransitionSystem
from yazelc.systems.visual_effects_system import VisualEffectsSystem


class InputSystem(esper.Processor):
    # List of processor types to remove on pause
    PROCESSOR_TYPES_PAUSE = [MovementSystem, ScriptSystem, CollisionSystem, CombatSystem, VisualEffectsSystem, TransitionSystem,
                             AnimationSystem]

    def __init__(self, controller: Controller):
        super().__init__()
        self.controller = controller
        self.is_paused = False
        self.processors_pause = None
        event_manager.subscribe(EventType.PAUSE, self.on_pause)

    def process(self):
        self.controller.process_input()

        if self.is_paused:
            for entity, (input_, _) in self.world.get_components(cmp.Input, cmp.Menu):
                input_.handle_input_function(entity, self.controller, self.world)
        else:
            for entity, input_ in self.world.get_component(cmp.Input):
                input_.handle_input_function(entity, self.controller, self.world)

    def on_pause(self):
        self.is_paused = not self.is_paused

        if self.is_paused:
            if not self.processors_pause:
                self.processors_pause = [self.world.get_processor(proc_type) for proc_type in self.PROCESSOR_TYPES_PAUSE]
            for proc in self.PROCESSOR_TYPES_PAUSE:
                self.world.remove_processor(proc)
            pause_menu.create_entity(self.world)
        else:
            for proc in self.processors_pause:
                self.world.add_processor(proc)
