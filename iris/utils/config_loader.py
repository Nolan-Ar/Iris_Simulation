"""
IRIS Configuration Loader
==========================

Utilities for loading and accessing configuration from YAML files.
"""

import yaml
from pathlib import Path
from typing import Any, Optional, Dict
import logging

logger = logging.getLogger(__name__)

# Global config cache
_config_cache: Optional[Dict[str, Any]] = None


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to config file (default: config.yaml in project root)

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file not found
        yaml.YAMLError: If config file is invalid
    """
    global _config_cache

    # Use cached config if available
    if _config_cache is not None and config_path is None:
        return _config_cache

    # Determine config path
    if config_path is None:
        # Try to find config.yaml in project root
        current_dir = Path(__file__).parent.parent.parent
        config_path = current_dir / "config.yaml"
    else:
        config_path = Path(config_path)

    # Check if file exists
    if not config_path.exists():
        logger.warning(f"Config file not found: {config_path}, using defaults")
        return get_default_config()

    # Load YAML
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        # Cache for future use
        _config_cache = config
        logger.info(f"Configuration loaded from {config_path}")

        return config

    except yaml.YAMLError as e:
        logger.error(f"Error parsing config file: {e}")
        raise


def get_config_value(
    *keys: str, default: Any = None, config: Optional[Dict] = None
) -> Any:
    """
    Get a configuration value using dot notation.

    Args:
        *keys: Configuration keys (e.g., 'simulation', 'population', 'default_size')
        default: Default value if key not found
        config: Configuration dict (if None, loads from file)

    Returns:
        Configuration value or default

    Example:
        >>> get_config_value('simulation', 'population', 'default_size')
        1000
    """
    if config is None:
        config = load_config()

    # Navigate through nested keys
    value = config
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default

    return value


def get_default_config() -> Dict[str, Any]:
    """
    Return default configuration if YAML file is not available.

    Returns:
        Default configuration dictionary
    """
    return {
        "simulation": {
            "population": {
                "default_size": 1000,
                "min_size": 10,
                "max_size": 1000000,
                "initial_mean_age": 36.0,
                "max_age": 90.0,
            },
            "economy": {
                "initial_total_V": 1000000.0,
                "universal_income_rate": 0.02,
                "transfer_probability": 0.1,
                "max_transfer_fraction": 0.1,
            },
            "businesses": {
                "enabled": True,
                "initial_count": 10,
                "salary_ratio": 0.40,
                "treasury_ratio": 0.60,
                "retention_threshold": 0.20,
            },
            "demographics": {
                "enabled": True,
                "birth_rate_base": 0.015,
                "death_rate_base": 0.01,
                "mortality_age_threshold": 70.0,
            },
            "catastrophes": {
                "enabled": False,
                "base_probability": 0.01,
                "max_magnitude": 0.5,
            },
            "oracle": {
                "enabled": True,
                "nft_creation_threshold": 100000.0,
                "equilibrium_tolerance": 0.05,
            },
        },
        "execution": {
            "default_steps": 100,
            "seed": None,
            "log_interval": 10,
            "save_history": True,
        },
        "performance": {
            "use_vectorized": True,
            "multiprocessing": False,
            "n_workers": 4,
            "batch_size": 1000,
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "file": "iris_simulation.log",
            "console": True,
            "file_enabled": True,
        },
        "output": {
            "results_dir": "simulation_results",
            "plots_dir": "plots",
            "data_dir": "data",
            "export_format": "json",
            "save_plots": True,
            "plot_format": "png",
        },
        "validation": {
            "enabled": True,
            "monte_carlo_runs": 100,
            "sensitivity_analysis": True,
            "statistical_tests": True,
            "confidence_level": 0.95,
        },
        "safety": {
            "min_positive_value": 1e-10,
            "max_value": 1e15,
            "epsilon": 1e-10,
            "check_nan": True,
            "check_inf": True,
        },
    }
