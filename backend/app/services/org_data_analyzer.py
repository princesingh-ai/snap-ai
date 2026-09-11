import json
import re

from app.inference.llama_client import LlamaClient


ORG_DATA_CLASSIFIER_PROMPT = """
You are an organizational-data access classifier.

Determine whether the user's request requires reading data from the organization's
protected data store.

Return ONLY valid JSON in this exact format:

{
  "requires_org_data": true,
  "resource_type": "finance"
}

Allowed resource_type values:
- "none"        -> no organizational data is required
- "public"      -> public organizational information
- "policies"    -> organizational policies, rules, guidelines, security policies
- "engineering" -> internal engineering, architecture, source code, technical docs
- "finance"     -> financial, revenue, expenses, budgets, financial reports

Rules:
- Do NOT decide whether the user is authorized.
- Do NOT decide the user's role.
- Do NOT grant or deny access.
- Only identify what type of organizational data would be needed.
- If no organizational data is needed, use "none".
- If uncertain, use "none".
"""


class OrgDataAnalyzer:
    def __init__(self, llama_client: LlamaClient, model: str):
        self.llama_client = llama_client
        self.model = model

    async def analyze(self, messages: list[dict]) -> dict:
        if not messages:
            return {
                "requires_org_data": False,
                "resource_type": "none",
            }

        user_message = messages[-1].get("content", "")

        if not isinstance(user_message, str) or not user_message.strip():
            return {
                "requires_org_data": False,
                "resource_type": "none",
            }

        response = await self.llama_client.chat(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": ORG_DATA_CLASSIFIER_PROMPT,
                },
                {
                    "role": "user",
                    "content": user_message,
                },
            ],
        )

        raw_result = response["choices"][0]["message"]["content"]

        result = self._parse_result(raw_result)

        print(f"[ORG DATA ANALYZER] QUERY: {user_message}")
        print(f"[ORG DATA ANALYZER] RESULT: {result}")

        return result

    @staticmethod
    def _parse_result(raw_result: str) -> dict:
        try:
            result = json.loads(raw_result)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", raw_result, re.DOTALL)

            if not match:
                return {
                    "requires_org_data": False,
                    "resource_type": "none",
                }

            try:
                result = json.loads(match.group(0))
            except json.JSONDecodeError:
                return {
                    "requires_org_data": False,
                    "resource_type": "none",
                }

        allowed_types = {
            "none",
            "public",
            "policies",
            "engineering",
            "finance",
        }

        resource_type = result.get("resource_type", "none")

        if resource_type not in allowed_types:
            resource_type = "none"

        requires_org_data = (
            result.get("requires_org_data") is True
            and resource_type != "none"
        )

        return {
            "requires_org_data": requires_org_data,
            "resource_type": resource_type,
        }