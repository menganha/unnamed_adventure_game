from yazelc import zesper

from yazelc.components import Script


class ScriptSystem(zesper.Processor):
    """ Handle all scripts (custom functions) that are called with certain delay """

    def process(self):
        for ent, (script) in self.world.get_component(Script):
            if script.delay > 0:
                script.delay -= 1
            if script.delay == 0:
                script.function(*script.args, self.world)
                self.world.remove_component(ent, Script)
