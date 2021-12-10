from yazelc import zesper
from yazelc.components import Input, Menu
from yazelc.controller import Controller


class MenuInputSystem(zesper.Processor):

    def __init__(self, controller: Controller):
        super().__init__()
        self.controller = controller

    def process(self):
        self.controller.process_input()

        for entity, (input_, _) in self.world.get_components(Input, Menu):
            input_.handle_input_function(entity, self.controller, self.world)
