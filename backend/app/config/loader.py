from pathlib import Path
import yaml

CONFIG_PATH = Path(__file__).resolve().parent.parent / "models.yaml"

def load_models() -> dict:
    """Load the model configurations from the models.yaml file."""
    with open(CONFIG_PATH, "r") as file:
        config = yaml.safe_load(file)

        return config.get("models", {}) # Return the "models" section of the configuration, or an empty dictionary if not found.