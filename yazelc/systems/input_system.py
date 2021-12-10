from yazelc import zesper
from yazelc.components import Input
from yazelc.controller import Controller


class InputSystem(zesper.Processor):

    def __init__(self, controller: Controller):
        super().__init__()
        self.controller = controller

    def process(self):
        self.controller.process_input()

        for entity, input_ in self.world.get_component(Input):
            input_.handle_input_function(entity, self.controller, self.world)