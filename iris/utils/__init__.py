"""
IRIS Utils Module
=================

Utilities for the IRIS economic simulation system including:
- Logging configuration
- Data validation helpers
- Math utilities with safety checks
- Configuration loading
"""

from iris.utils.logging_config import setup_logging, get_logger
from iris.utils.validation import (
    ValidationError,
    validate_positive,
    validate_non_negative,
    validate_range,
    validate_probability,
    safe_divide,
    safe_mean,
    clip_value,
)
from iris.utils.math_helpers import (
    safe_gini,
    safe_std,
    safe_sum,
    check_nan_inf,
    replace_nan_inf,
)
from iris.utils.config_loader import load_config, get_config_value

__all__ = [
    # Logging
    "setup_logging",
    "get_logger",
    # Validation
    "ValidationError",
    "validate_positive",
    "validate_non_negative",
    "validate_range",
    "validate_probability",
    "safe_divide",
    "safe_mean",
    "clip_value",
    # Math
    "safe_gini",
    "safe_std",
    "safe_sum",
    "check_nan_inf",
    "replace_nan_inf",
    # Config
    "load_config",
    "get_config_value",
]
