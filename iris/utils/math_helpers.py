"""
IRIS Math Helpers
=================

Mathematical utility functions with built-in safety checks
to prevent division by zero, NaN, and infinity.
"""

import numpy as np
from typing import Union, Tuple
from iris.utils.validation import EPSILON


def safe_gini(values: np.ndarray, epsilon: float = EPSILON) -> float:
    """
    Safely compute Gini coefficient, avoiding division by zero.

    The Gini coefficient measures inequality in a distribution.
    Returns 0.0 if the distribution is empty or has zero total.

    Args:
        values: Array of values (e.g., wealth)
        epsilon: Minimum total to avoid div/0

    Returns:
        Gini coefficient (0.0 to 1.0)
    """
    # Handle empty or zero-sum arrays
    if values.size == 0:
        return 0.0

    # Remove negative values (they don't make sense for Gini)
    values = values[values >= 0]

    if values.size == 0:
        return 0.0

    # Sort values
    sorted_values = np.sort(values)
    n = sorted_values.size

    # Check for zero total
    total = np.sum(sorted_values)
    if total < epsilon:
        return 0.0

    # Compute Gini using the standard formula
    # Gini = (2 * sum(i * x_i)) / (n * sum(x_i)) - (n + 1) / n
    index = np.arange(1, n + 1)
    gini = (2.0 * np.sum(index * sorted_values)) / (n * total) - (n + 1) / n

    # Clamp to valid range [0, 1]
    return float(np.clip(gini, 0.0, 1.0))


def safe_std(
    arr: np.ndarray, default: float = 0.0, epsilon: float = EPSILON
) -> float:
    """
    Safely compute standard deviation.

    Args:
        arr: Input array
        default: Default value if array is empty
        epsilon: Minimum variance to return non-zero

    Returns:
        Standard deviation or default
    """
    if arr.size == 0:
        return default

    std = float(np.std(arr))

    # Avoid returning tiny values that are essentially zero
    if std < epsilon:
        return 0.0

    return std


def safe_sum(arr: np.ndarray, default: float = 0.0) -> float:
    """
    Safely compute sum, handling empty arrays.

    Args:
        arr: Input array
        default: Default if array is empty

    Returns:
        Sum or default
    """
    if arr.size == 0:
        return default
    return float(np.sum(arr))


def check_nan_inf(
    arr: Union[np.ndarray, float], name: str = "array"
) -> Tuple[bool, str]:
    """
    Check if array or value contains NaN or Inf.

    Args:
        arr: Array or value to check
        name: Name for error messages

    Returns:
        Tuple (has_issues, message)
    """
    if isinstance(arr, np.ndarray):
        has_nan = np.any(np.isnan(arr))
        has_inf = np.any(np.isinf(arr))

        if has_nan and has_inf:
            return True, f"{name} contains both NaN and Inf values"
        elif has_nan:
            return True, f"{name} contains NaN values"
        elif has_inf:
            return True, f"{name} contains Inf values"
        else:
            return False, ""
    else:
        if np.isnan(arr):
            return True, f"{name} is NaN"
        elif np.isinf(arr):
            return True, f"{name} is Inf"
        else:
            return False, ""


def replace_nan_inf(
    arr: np.ndarray, nan_value: float = 0.0, inf_value: float = 0.0
) -> np.ndarray:
    """
    Replace NaN and Inf values in an array.

    Args:
        arr: Input array
        nan_value: Replacement for NaN
        inf_value: Replacement for Inf

    Returns:
        Cleaned array
    """
    arr = arr.copy()
    arr[np.isnan(arr)] = nan_value
    arr[np.isinf(arr)] = inf_value
    return arr


def safe_log(
    arr: Union[np.ndarray, float], epsilon: float = EPSILON
) -> Union[np.ndarray, float]:
    """
    Safely compute logarithm, avoiding log(0) and log(negative).

    Args:
        arr: Input value(s)
        epsilon: Minimum value for log

    Returns:
        Logarithm with safe handling
    """
    if isinstance(arr, np.ndarray):
        safe_arr = np.maximum(arr, epsilon)
        return np.log(safe_arr)
    else:
        safe_val = max(arr, epsilon)
        return np.log(safe_val)


def normalize_array(
    arr: np.ndarray, target_sum: float = 1.0, epsilon: float = EPSILON
) -> np.ndarray:
    """
    Normalize an array to sum to a target value.

    Args:
        arr: Input array
        target_sum: Target sum
        epsilon: Minimum sum to avoid div/0

    Returns:
        Normalized array
    """
    if arr.size == 0:
        return arr

    current_sum = np.sum(arr)

    if current_sum < epsilon:
        # If sum is zero, return uniform distribution
        return np.full_like(arr, target_sum / arr.size)

    return arr * (target_sum / current_sum)
