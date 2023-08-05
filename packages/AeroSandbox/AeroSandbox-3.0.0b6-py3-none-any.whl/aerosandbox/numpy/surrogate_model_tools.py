import aerosandbox.numpy as _np
from typing import Tuple, Union


def softmax(value1, value2, hardness=1):
    """
    A smooth maximum between two functions. Also referred to as the logsumexp() function.
    Useful because it's differentiable and preserves convexity!
    Great writeup by John D Cook here:
        https://www.johndcook.com/soft_maximum.pdf
    :param value1: Value of function 1.
    :param value2: Value of function 2.
    :param hardness: Hardness parameter. Higher values make this closer to max(x1, x2).
    :return: Soft maximum of the two supplied values.
    """
    if hardness <= 0:
        raise ValueError("The value of `hardness` must be positive.")
    value1 = value1 * hardness
    value2 = value2 * hardness
    max = _np.fmax(value1, value2)
    min = _np.fmin(value1, value2)
    out = max + _np.log(1 + _np.exp(min - max))
    out = out / hardness
    return out


def sigmoid(
        x,
        sigmoid_type: str = "tanh",
        normalization_range: Tuple[Union[float, int], Union[float, int]] = (0, 1)
):
    """
    A sigmoid function. From Wikipedia (https://en.wikipedia.org/wiki/Sigmoid_function):
        A sigmoid function is a mathematical function having a characteristic "S"-shaped curve
        or sigmoid curve.

    Args:
        x: The input
        sigmoid_type: Type of sigmoid function to use [str]. Can be one of:
            * "tanh" or "logistic" (same thing)
            * "arctan"
            * "polynomial"
        normalization_type: Range in which to normalize the sigmoid, shorthanded here in the
            documentation as "N". This parameter is given as a two-element tuple (min, max).

            After normalization:
                >>> sigmoid(-Inf) == normalization_range[0]
                >>> sigmoid(Inf) == normalization_range[1]

            * In the special case of N = (0, 1):
                >>> sigmoid(-Inf) == 0
                >>> sigmoid(Inf) == 1
                >>> sigmoid(0) == 0.5
                >>> d(sigmoid)/dx at x=0 == 0.5
            * In the special case of N = (-1, 1):
                >>> sigmoid(-Inf) == -1
                >>> sigmoid(Inf) == 1
                >>> sigmoid(0) == 0
                >>> d(sigmoid)/dx at x=0 == 1

    Returns: The value of the sigmoid.
    """
    ### Sigmoid equations given here under the (-1, 1) normalization:
    if sigmoid_type == ("tanh" or "logistic"):
        # Note: tanh(x) is simply a scaled and shifted version of a logistic curve; after
        #   normalization these functions are identical.
        s = _np.tanh(x)
    elif sigmoid_type == "arctan":
        s = 2 / _np.pi * _np.arctan(_np.pi / 2 * x)
    elif sigmoid_type == "polynomial":
        s = x / (1 + x ** 2) ** 0.5
    else:
        raise ValueError("Bad value of parameter 'type'!")

    ### Normalize
    min = normalization_range[0]
    max = normalization_range[1]
    s_normalized = s * (max - min) / 2 + (max + min) / 2

    return s_normalized


def blend(
        switch: float,
        value_switch_high,
        value_switch_low,
):
    """
    Smoothly blends between two values on the basis of some switch function.

    This function is similar in usage to numpy.where (documented here:
    https://numpy.org/doc/stable/reference/generated/numpy.where.html) , except that
    instead of using a boolean as to switch between the two values, a float is used to
    smoothly transition between the two in a differentiable manner.

    Before using this function, be sure to understand the difference between this and
    smoothmax(), and choose the correct one.

    Args:
        switch: A value that acts as a "switch" between the two values [float].
            If switch is -Inf, value_switch_low is returned.
            If switch is Inf, value_switch_high is returned.
            If switch is 0, the mean of value_switch_low and value_switch_high is returned.
            If switch is 1, the return value is roughly (0.88 * value_switch_high + 0.12 * value_switch_low).
            If switch is -1, the return value is roughly (0.88 * value_switch_low + 0.12 * value_switch_high).
        value_switch_high: Value to be returned when switch is high. Can be a float or an array.
        value_switch_low: Value to be returned when switch is low. Can be a float or an array.

    Returns: A value that is a blend between value_switch_low and value_switch_high, with the weighting dependent
        on the value of the 'switch' parameter.

    """
    blend_function = lambda x: sigmoid(
        x,
        normalization_range=(0, 1)
    )
    weight_to_value_switch_high = blend_function(switch)

    blend_value = (
            value_switch_high * weight_to_value_switch_high +
            value_switch_low * (1 - weight_to_value_switch_high)
    )

    return blend_value
