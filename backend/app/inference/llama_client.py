import httpx


class LlamaClient:

    def __init__(self, base_url: str):

        self.base_url = base_url

        self.client = httpx.AsyncClient(
            timeout=120
        )

    async def chat(self, messages: list[dict], model: str) -> dict:

        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
        }

        response = await self.client.post(
            f"{self.base_url}/v1/chat/completions",
            json=payload,
        )

        response.raise_for_status()

        return response.json()

    async def chat_stream(self, messages: list[dict], model: str, request_body: dict):

        payload = dict(request_body)

        payload["model"] = model
        payload["messages"] = messages
        payload["stream"] = True

        async with self.client.stream(
            "POST",
            f"{self.base_url}/v1/chat/completions",
            json=payload,
        ) as response:

            response.raise_for_status()

            async for line in response.aiter_lines():

                if line:
                    yield line + "\n"

    async def close(self):

        await self.client.aclose()