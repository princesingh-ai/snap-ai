from fastmcp import Client


class MCPClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def read_file(self, path: str, access_token: str) -> str:
        async with Client(
            self.base_url,
            auth=access_token,
        ) as client:
            result = await client.call_tool(
                "read_file",
                {"path": path},
            )

        if result.is_error:
            raise PermissionError(
                result.content[0].text
                if result.content
                else "MCP tool call failed."
            )

        return result.content[0].text