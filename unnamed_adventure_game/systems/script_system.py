import esper

from unnamed_adventure_game.components import Script


class ScriptSystem(esper.Processor):

    def process(self):
        """ Process all scripts """
        for ent, (script) in self.world.get_component(Script):
            if script.delay > 0:
                script.delay -= 1
            if script.delay == 0:
                script.function(*script.args, self.world)
                self.world.remove_component(ent, Script)
