# class TaskAnalyzer:
#     def analyze(self, messages: list[dict]) -> dict:
#         if not messages:
#             return "general"

#         user_message = messages[-1]["content"].lower()

#         if self.is_coding_task(user_message):
#             return "coding"

#         if self.is_reasoning_task(user_message):
#             return "reasoning"

#         return "general"

#     def is_coding_task(self, text: str) -> bool:
#         keywords = ["write code", "write a program", "python code", "javascript code", "typescript code", "debug", "debuugging", "fix this code", "code review", "implement", "function", "class", "api", "api endpoint", "sql query", "code", "generate code", "generate a function", "generate a class", "generate an api endpoint", "generate an sql query"]
#         return any(keyword in text for keyword in keywords)

#     def is_reasoning_task(self, text: str) -> bool:
#         keywords = ["analyze", "explain", "reasoning", "logic", "problem-solving", "critical thinking", "evaluate", "assess", "interpret", "deduce", "infer", "why", "derive", "calculate", "solve", "decision-making", "judgment", "conclusion", "synthesize", "compare", "contrast", "predict", "hypothesize"]
#         return any(keyword in text for keyword in keywords)


from app.inference.llama_client import LlamaClient

CLASSIFIER_PROMPT = """
You are a classification model.

Your ONLY job is to classify the user's request.

You MUST return exactly one of these words:

coding
reasoning
general

Never answer the user's request.
Never write code.
Never explain your decision.

Examples:

User: write a python function to add two numbers
coding

User: debug this javascript code
coding

User: create a SQL query to find users
coding

User: calculate 25 percent of 400
reasoning

User: compare two algorithms
reasoning

User: solve this logic puzzle
reasoning

User: what is the capital of France
general

User: summarize this document
general

User: translate this sentence
general

Return ONLY one word.
"""


class TaskAnalyzer:
    def __init__(self, llama_client: LlamaClient, model: str):
        self.llama_client = llama_client
        self.model = model

    async def analyze(self, messages: list[dict]) -> str:
        if not messages:
            return "general"

        user_message = messages[-1].get("content", "")
        if not user_message:
            return "general"

        response = await self.llama_client.chat(model=self.model, messages=[{"role": "system", "content": CLASSIFIER_PROMPT}, {"role": "user", "content": user_message}])
        result = response["choices"][0]["message"]["content"]

        print(f"[TASK ANALYZER] QUERY: {user_message}")
        print(f"[TASK ANALYZER] RESULT: {result}")

        return self.normalize(result)

    @staticmethod
    def normalize(result: str) -> str:
        result = result.strip().lower()

        if result in {"coding", "reasoning", "general"}:
            return result

        return "general"