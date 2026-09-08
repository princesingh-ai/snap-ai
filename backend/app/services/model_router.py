from app.config.loader import load_models

class ModelRouter:
    def __init__(self):
        self.models = load_models()

    def route(self, task: str) -> str:

        for model_key, model in self.models.items():
            print(f"[DEBUG]CHECKING MODEL:{model_key}")
            print(f"[DEBUG]CAPABILITIES: {model.get("capabilities", [])}")

            if not model.get("enabled", False):
                continue

            capabilities = model.get("capabilities", [])

            if task in capabilities:
                print(f"[DEBUG] ROUTING TO MODEL: {model_key}")
                return model_key

        if "general" in self.models and self.models["general"].get("enabled", False):
            print("[DEBUG] ROUTING TO GENERAL MODEL")
            return "general"

        raise RuntimeError(f"No enabled model found for task: {task}")

    def route_document_image(self) -> str:
        model_key = "document_image"

        model = self.models.get(model_key)

        if not model:
            raise RuntimeError(
                "Document/image model is not configured.")

        if not model.get("enabled", False):
            raise RuntimeError(
                "Document/image model is disabled.")

        print("[DEBUG] ROUTING DOCUMENT/IMAGE TO MODEL: document_image")

        return model_key