"""Blender path configuration loading for real Blender tests.

This module provides functionality to load and validate Blender executable
configurations from JSON files and environment variables.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

# Default path to the Blender configuration file
DEFAULT_CONFIG_PATH = Path(__file__).parent.parent.parent / "blender-paths.json"

logger = logging.getLogger(__name__)


def load_blender_configs(config_path: Path | str | None = None) -> list[dict[str, Any]]:
    """Load Blender executable configurations from file and environment variables.

    Args:
        config_path: Optional path to the configuration file. If not provided,
            uses BLENDER_TEST_PATHS environment variable or default path.

    Returns:
        A list of Blender configuration dictionaries. Each dict contains:
        - version: Blender version string (e.g., "4.2.17")
        - path: Absolute path to the Blender executable
        - tags: Optional list of tags (e.g., ["lts", "baseline"])

    Examples:
        >>> configs = load_blender_configs()
        >>> for config in configs:
        ...     print(f"{config['version']}: {config['path']}")
    """
    configs: list[dict[str, Any]] = []

    # Determine config file path
    if config_path is None:
        env_path = os.getenv("BLENDER_TEST_PATHS")
        if env_path:
            config_path = Path(env_path)
        else:
            config_path = DEFAULT_CONFIG_PATH
    else:
        config_path = Path(config_path)

    # Load from file if exists
    if config_path.exists():
        try:
            with open(config_path, encoding="utf-8") as f:
                data = json.load(f)
                file_configs = data.get("blender_executables", [])
                for config in file_configs:
                    if _validate_and_normalize_config(config):
                        configs.append(config)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Failed to load Blender config from %s: %s", config_path, e)
    else:
        logger.debug("No Blender config file found at %s", config_path)

    # Add BLENDER_EXECUTABLE environment variable if set
    single_path = os.getenv("BLENDER_EXECUTABLE")
    if single_path:
        config = {"path": single_path, "version": "env", "tags": ["env"]}
        if _validate_and_normalize_config(config):
            configs.append(config)

    return configs


def _validate_and_normalize_config(config: dict[str, Any]) -> bool:
    """Validate and normalize a Blender configuration.

    Args:
        config: Configuration dictionary to validate.

    Returns:
        True if the configuration is valid, False otherwise.
    """
    if "path" not in config:
        logger.warning("Blender config missing 'path' field: %s", config)
        return False

    path = Path(config["path"])

    # Normalize path
    config["path"] = str(path.resolve())

    # Check existence
    if not path.exists():
        logger.warning("Blender executable not found: %s", config["path"])
        return False

    # Check if executable
    if not os.access(config["path"], os.X_OK):
        logger.warning("Blender path is not executable: %s", config["path"])
        return False

    # Ensure version field
    if "version" not in config:
        detected_version = _detect_blender_version(config["path"])
        if detected_version:
            config["version"] = detected_version
        else:
            config["version"] = "unknown"

    # Ensure tags field
    if "tags" not in config:
        config["tags"] = []

    return True


def _detect_blender_version(blender_path: str) -> str | None:
    """Detect Blender version by running the executable.

    Args:
        blender_path: Path to the Blender executable.

    Returns:
        Version string if detected, None otherwise.
    """
    import subprocess

    try:
        result = subprocess.run(
            [blender_path, "--version"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        # Blender output format: "Blender 4.2.17"
        for line in result.stdout.splitlines():
            if line.startswith("Blender "):
                version = line.split()[1]
                return version
    except (OSError, subprocess.TimeoutExpired) as e:
        logger.debug("Failed to detect Blender version from %s: %s", blender_path, e)

    return None
