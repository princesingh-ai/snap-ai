import httpx

class LlamaClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = base_url.rstrip("/")  # Remove trailing slash if present

    async def chat(self, messages: list[dict], model: str) -> dict:
        """send a chat request to the llama server and return the response"""
        payload = {"model": model, "messages": messages}

        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(f"{self.client}/v1/chat/completions", json=payload)
            response.raise_for_status() # Raise an exception for HTTP errors
            return response.json()