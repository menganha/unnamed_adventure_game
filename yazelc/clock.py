from collections.abc import Callable
from typing import Any


class Timer:
    """
    Container of the callback, arguments and delay of the timer event
    """

    def __init__(self, delay: int, repeat: bool, callback: Callable, *args: Any, **kwargs: Any):
        self.delay = delay
        self.repeat = repeat
        self.callback = callback
        self.args = args
        self.kwargs = kwargs
        self.ticks_to_reset = delay


class Clock:

    def __init__(self):
        self.timer_events: list[Timer] = list()

    def add_timer(self, timer: Timer):
        self.timer_events.append(timer)

    def tick(self):
        idx_timers_to_remove = list()
        for idx, timer in enumerate(self.timer_events):
            if timer.ticks_to_reset <= 0:
                timer.callback(*timer.args, **timer.kwargs)
                if timer.repeat:
                    timer.ticks_to_reset = timer.delay
                else:
                    idx_timers_to_remove.append(idx)
                continue
            timer.ticks_to_reset -= 1

        if idx_timers_to_remove:
            self.timer_events = [timer for idx, timer in enumerate(self.timer_events) if idx not in idx_timers_to_remove]
