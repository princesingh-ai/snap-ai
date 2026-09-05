class TaskAnalyzer:
    def analyze(self, messages: list[dict]) -> dict:
        if not messages:
            return "general"

        user_message = messages[-1]["content"].lower()

        if self.is_coding_task(user_message):
            return "coding"

        if self.is_reasoning_task(user_message):
            return "reasoning"

        return "general"

    def is_coding_task(self, text: str) -> bool:
        keywords = ["write code", "write a program", "python code", "javascript code", "typescript code", "debug", "debuugging", "fix this code", "code review", "implement", "function", "class", "api", "api endpoint", "sql query", "code", "generate code", "generate a function", "generate a class", "generate an api endpoint", "generate an sql query"]
        return any(keyword in text for keyword in keywords)

    def is_reasoning_task(self, text: str) -> bool:
        keywords = ["analyze", "explain", "reasoning", "logic", "problem-solving", "critical thinking", "evaluate", "assess", "interpret", "deduce", "infer", "why", "derive", "calculate", "solve", "decision-making", "judgment", "conclusion", "synthesize", "compare", "contrast", "predict", "hypothesize"]
        return any(keyword in text for keyword in keywords)