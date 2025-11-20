"""
IRIS Validation Utilities
==========================

Validation helpers to prevent common errors like division by zero,
negative values, NaN, and infinity.
"""

import numpy as np
from typing import Union, Optional

# Safety constants
EPSILON = 1e-10
MIN_POSITIVE_VALUE = 1e-10
MAX_VALUE = 1e15


class ValidationError(ValueError):
    """Custom exception for validation errors."""

    pass


def validate_positive(
    value: Union[float, int, np.ndarray],
    name: str = "value",
    min_value: float = MIN_POSITIVE_VALUE,
) -> Union[float, int, np.ndarray]:
    """
    Validate that a value is positive (> 0).

    Args:
        value: Value to validate
        name: Name for error messages
        min_value: Minimum acceptable positive value

    Returns:
        The validated value

    Raises:
        ValidationError: If value is not positive
    """
    if isinstance(value, np.ndarray):
        if np.any(value <= 0):
            raise ValidationError(f"{name} must be positive, got array with negative/zero values")
        if np.any(value < min_value):
            raise ValidationError(f"{name} must be >= {min_value}")
    else:
        if value <= 0:
            raise ValidationError(f"{name} must be positive, got {value}")
        if value < min_value:
            raise ValidationError(f"{name} must be >= {min_value}, got {value}")
    return value


def validate_non_negative(
    value: Union[float, int, np.ndarray], name: str = "value"
) -> Union[float, int, np.ndarray]:
    """
    Validate that a value is non-negative (>= 0).

    Args:
        value: Value to validate
        name: Name for error messages

    Returns:
        The validated value

    Raises:
        ValidationError: If value is negative
    """
    if isinstance(value, np.ndarray):
        if np.any(value < 0):
            raise ValidationError(f"{name} must be non-negative, got array with negative values")
    else:
        if value < 0:
            raise ValidationError(f"{name} must be non-negative, got {value}")
    return value


def validate_range(
    value: Union[float, int],
    min_val: float,
    max_val: float,
    name: str = "value",
    inclusive: bool = True,
) -> Union[float, int]:
    """
    Validate that a value is within a range.

    Args:
        value: Value to validate
        min_val: Minimum value
        max_val: Maximum value
        name: Name for error messages
        inclusive: If True, endpoints are included

    Returns:
        The validated value

    Raises:
        ValidationError: If value is out of range
    """
    if inclusive:
        if not (min_val <= value <= max_val):
            raise ValidationError(f"{name} must be in [{min_val}, {max_val}], got {value}")
    else:
        if not (min_val < value < max_val):
            raise ValidationError(f"{name} must be in ({min_val}, {max_val}), got {value}")
    return value


def validate_probability(value: Union[float, int], name: str = "probability") -> float:
    """
    Validate that a value is a valid probability (0 <= p <= 1).

    Args:
        value: Probability to validate
        name: Name for error messages

    Returns:
        The validated probability

    Raises:
        ValidationError: If not a valid probability
    """
    return validate_range(value, 0.0, 1.0, name, inclusive=True)


def safe_divide(
    numerator: Union[float, np.ndarray],
    denominator: Union[float, np.ndarray],
    default: float = 0.0,
    epsilon: float = EPSILON,
) -> Union[float, np.ndarray]:
    """
    Safely divide two numbers, avoiding division by zero.

    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if denominator is zero
        epsilon: Minimum denominator value to avoid div/0

    Returns:
        Result of division or default value
    """
    if isinstance(denominator, np.ndarray):
        result = np.zeros_like(denominator, dtype=float)
        mask = np.abs(denominator) >= epsilon
        result[mask] = numerator[mask] / denominator[mask] if isinstance(numerator, np.ndarray) else numerator / denominator[mask]
        result[~mask] = default
        return result
    else:
        if abs(denominator) < epsilon:
            return default
        return numerator / denominator


def safe_mean(
    arr: np.ndarray, default: float = 0.0, epsilon: float = EPSILON
) -> float:
    """
    Safely compute mean of array, avoiding division by zero.

    Args:
        arr: Input array
        default: Default value if array is empty
        epsilon: Minimum sum to avoid div/0

    Returns:
        Mean or default value
    """
    if arr.size == 0:
        return default
    total = np.sum(arr)
    if abs(total) < epsilon and arr.size == 0:
        return default
    return float(np.mean(arr))


def clip_value(
    value: Union[float, np.ndarray],
    min_val: float = -MAX_VALUE,
    max_val: float = MAX_VALUE,
) -> Union[float, np.ndarray]:
    """
    Clip a value to prevent overflow.

    Args:
        value: Value to clip
        min_val: Minimum value
        max_val: Maximum value

    Returns:
        Clipped value
    """
    if isinstance(value, np.ndarray):
        return np.clip(value, min_val, max_val)
    else:
        return max(min_val, min(max_val, value))
