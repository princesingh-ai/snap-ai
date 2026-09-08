from pathlib import Path

import yaml


CONFIG_PATH = Path(__file__).resolve().parent / "models.yaml"


def load_config() -> dict:
    """Load the complete model configuration."""
    with open(CONFIG_PATH, "r") as file:
        return yaml.safe_load(file) or {}


def load_models() -> dict:
    """Load the model configurations."""
    config = load_config()
    return config.get("models", {})


def load_task_analyzer() -> dict:
    """Load the task analyzer configuration."""
    config = load_config()
    return config.get("task_analyzer", {})