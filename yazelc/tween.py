""" Tweening functions """
from enum import Enum, auto


class TweenFunction(Enum):
    EASE_OUT_CUBIC = auto()
    EASE_OUT_QUINT = auto()
    EASE_OUT_EXPO = auto()
    EASE_IN_OUT_QUAD = auto()
    EASE_IN_QUAD = auto()


def tweening(time: float, tween_function: TweenFunction):
    """ tween function with argument from 0.0 to 1.0 """
    if tween_function == TweenFunction.EASE_OUT_CUBIC:
        return _ease_out_cubic(time)
    elif tween_function == TweenFunction.EASE_OUT_EXPO:
        return _ease_out_expo(time)
    elif tween_function == TweenFunction.EASE_IN_OUT_QUAD:
        return _ease_in_out_quad(time)
    elif tween_function == TweenFunction.EASE_IN_QUAD:
        return _ease_in_quad(time)
    else:
        raise NotImplementedError(f'Tween function {tween_function.name} not implemented')


def _ease_out_cubic(time: float):
    """ tween function with argument from 0.0 to 1.0 """
    time = time - 1
    return time ** 3 + 1


def _ease_in_out_quad(n):
    if n < 0.5:
        return 2 * n ** 2
    else:
        n = n * 2 - 1
        return -0.5 * (n * (n - 2) - 1)


def _ease_in_quad(n):
    return n ** 2


def _ease_out_expo(time: float):
    """ tween function with argument from 0.0 to 1.0 """
    if time == 1:
        return 1
    else:
        return -(2 ** (-10 * time)) + 1
