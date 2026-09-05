# from app.config.loader import load_models
# from app.inference.llama_client import LlamaClient

# class ModelService:
#     def __init__(self, llama_client: LlamaClient):
#         self.llama_client = llama_client
#         self.models = load_models() # load the model confgs from the models.yaml file

#     async def chat(self, model_key: str, messages: list[dict]) -> dict:

#         print(f"[DEBUG] MODEL SERVICE: {model_key}")
#         print(f"[DEBUG] AVAILABLE MODELS: {list(self.models.keys())}")

#         if model_key not in self.models:
#             raise ValueError(f"Unknown model: {model_key} Available models: {list(self.models.keys())}")

#         model = self.models[model_key]

#         print(f"[DEBUG] SERVICE ACTUAL MODEL: {model["name"]}")

#         if not model.get("enabled", False):
#             raise ValueError(f"Model '{model_key}' is disabled.")

#         return await self.llama_client.chat(model=model["name"], messages=messages)


from app.config.loader import load_models
from app.inference.llama_client import LlamaClient


class ModelService:

    def __init__(self, llama_client: LlamaClient):

        self.llama_client = llama_client
        self.models = load_models()

    def get_model_name(self, model_key: str) -> str:

        if model_key not in self.models:
            raise ValueError(
                f"Unknown model: {model_key}. "
                f"Available models: {list(self.models.keys())}")

        model = self.models[model_key]

        if not model.get("enabled", False):
            raise ValueError(f"Model '{model_key}' is disabled.")

        return model["name"]

    async def chat(self, model_key: str, messages: list[dict]) -> dict:

        model_name = self.get_model_name(model_key)

        return await self.llama_client.chat(
            model=model_name,
            messages=messages)

    async def chat_stream(self,
        model_key: str,
        messages: list[dict],
        request_body: dict):

        model_name = self.get_model_name(model_key)

        async for chunk in self.llama_client.chat_stream(
            model=model_name,
            messages=messages,
            request_body=request_body):
            yield chunk