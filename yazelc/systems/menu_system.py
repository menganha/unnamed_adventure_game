import esper

from yazelc.pause_menu import PauseMenu


class MenuSystem(esper.Processor):

    def __init__(self):
        super().__init__()
        self.pause_menu = PauseMenu()

    def process(self):
        if self.pause_menu.entity:
            pass
