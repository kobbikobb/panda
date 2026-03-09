"""Configuration loading for the application."""

from pathlib import Path
from typing import Any

import yaml


def get_config_path(filename: str) -> Path:
    base_dir = Path(__file__).parent.parent
    return base_dir / "config" / filename


def load_yaml(filename: str) -> dict[str, Any]:
    path = get_config_path(filename)
    if not path.exists():
        return {}
    with open(path) as f:
        return yaml.safe_load(f) or {}


def load_system_prompts() -> dict[str, str]:
    return load_yaml("system_prompts.yaml")


def get_system_prompt(name: str = "default") -> str:
    prompts = load_system_prompts()
    return prompts.get(name, prompts.get("default", "You are a helpful assistant."))
