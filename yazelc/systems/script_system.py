from yazelc import zesper
from yazelc.components import Timer
from yazelc.event import ClockEvent


class ClockSystem(zesper.Processor):
    """ Handle components indicating that a signal should be sent at a delayed time or at regular intervals[  """

    def process(self):
        for ent, (timer) in self.world.get_component(Timer):
            if timer.tick > 0:
                timer.tick -= 1
            if timer.tick == 0:
                event = ClockEvent(ent, **timer.kwargs)  # TODO: Will these events be necessary at all?
                self.events.append(event)
                if timer.callback_index < len(timer.callbacks):
                    timer.callbacks[timer.callback_index](**timer.kwargs)
                    timer.tick = timer.delays[timer.callback_index]
                    timer.callback_index += 1
                else:
                    self.world.remove_component(ent, Timer)
