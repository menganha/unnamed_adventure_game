import esper
from components import Input


class InputSystem(esper.Processor):

    def process(self):
        for ent, input_component in self.world.get_component(Input):
            input_component.process(ent)
