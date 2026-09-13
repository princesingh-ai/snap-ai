from fastmcp import Client


class MCPClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def search_files(
        self,
        query: str,
        access_token: str,
    ) -> list[str]:
        async with Client(
            self.base_url,
            auth=access_token,
        ) as client:
            result = await client.call_tool(
                "search_files",
                {"query": query},
            )

        if result.is_error:
            raise PermissionError(
                result.content[0].text
                if result.content
                else "MCP tool call failed."
            )

        return result.data or []

    async def read_file(
        self,
        path: str,
        access_token: str,
    ) -> str:
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

        return result.data

    async def retrieve_context(
        self,
        query: str,
        resource_type: str,
        access_token: str,
    ) -> str:
        search_terms = [
            term
            for term in query.lower().split()
            if len(term) >= 3
        ]

        found_files = set()

        for term in search_terms:
            files = await self.search_files(
                query=term,
                access_token=access_token,
            )

            prefix = f"{resource_type}/"

            for path in files:
                if (
                    path.startswith(prefix)
                    and path.lower().endswith(".txt")
                ):
                    found_files.add(path)

        if not found_files:
            return ""

        context_parts = []

        for path in sorted(found_files):
            content = await self.read_file(
                path=path,
                access_token=access_token,
            )

            context_parts.append(
                f"--- {path} ---\n{content}"
            )

        return "\n\n".join(context_parts)