from collections import deque

from yazelc import zesper
from yazelc.components import Input
from yazelc.controller import Controller
from yazelc.event import Event


class InputMessage:
    def __init__(self, entity_id: int, controller: Controller, world: zesper.World, event_list: deque[Event]):
        self.ent_id = entity_id
        self.controller = controller
        self.world = world
        self.event_list = event_list


class InputSystem(zesper.Processor):
    """ Uses direct callback to process the input """

    def __init__(self, controller: Controller):
        super().__init__()
        self.controller = controller

    def process(self):
        self.controller.process_input()

        for entity, input_ in self.world.get_component(Input):
            if input_.block_counter != 0:
                input_.block_counter -= 1
            else:
                input_message = InputMessage(entity, self.controller, self.world, self.events)
                input_.handle_input_function(input_message)
