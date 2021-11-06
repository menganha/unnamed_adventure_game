import esper

from unnamed_adventure_game.components import Animation, State, Renderable
from unnamed_adventure_game.utils.game import Direction, Status


class AnimationSystem(esper.Processor):

    def process(self):
        for ent, (animation, renderable, state) in self.world.get_components(Animation, Renderable, State):
            renderable.image = animation.strips \
                .get(state.status, Status.IDLE) \
                .get(state.direction, Direction.SOUTH) \
                .next()
