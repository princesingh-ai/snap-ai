import httpx

class LlamaClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=120)

    async def chat(self, messages: list[dict], model: str) -> dict:
        """send a chat request to the llama server and return the response"""
        payload = {"model": model, "messages": messages}
        response = await self.client.post(f"{self.base_url}/v1/chat/completions", json=payload)

        response.raise_for_status() # Raise an exception for HTTP errors
        return response.json()

    async def close(self):
        """Close the Http client session"""
        await self.client.aclose()