from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

from app.inference.llama_client import LlamaClient
from app.services.model_services import ModelService
from app.services.task_analyzer import TaskAnalyzer
from app.services.model_router import ModelRouter

app = FastAPI(title="snap", description="A simple API for interacting with the LLaMA model", version="1.0.0")

llama = LlamaClient(base_url="http://localhost:8080")
model_service = ModelService(llama_client=llama)
task_analyzer = TaskAnalyzer(llama_client=llama, model="ggml-org/gemma-4-E2B-it-GGUF:Q8_0")
model_router = ModelRouter()

class Message(BaseModel):
    """A message in the chat conversation, consisting of a role and content."""
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: list[Message]

@app.get("/health", summary="Health Check", description="Check if the API is running")
async def health_check():
    return {"status": "Ok"}

@app.post("/api/chat", summary="Chat with Models", description="Send a chat request to the llama-server and receive a response from the models")
async def chat(request: ChatRequest):
    """Send a chat request to the llama-server and receive a response from the models."""

    messages = [{"role": message.role,
                 "content": message.content} for message in request.messages]

    task = await task_analyzer.analyze(messages)

    model_key = model_router.route(task)

    response = await model_service.chat(model_key=model_key, messages=messages)
    return {"task": task, "model": model_key, "response": response}

@app.post("/v1/chat/completions")
async def chat_completions(request: dict):

    messages = request.get("messages", [])
    task = await task_analyzer.analyze(messages)
    model_key = model_router.route(task)

    print(f"[DEBUG] TASK: {task}")
    print(f"[DEBUG] MODEL: {model_key}")

    if request.get("stream", False):

        async def generate():

            async for chunk in model_service.chat_stream(model_key=model_key, messages=messages, request_body=request):
                yield chunk

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"}
        )

    return await model_service.chat(model_key=model_key, messages=messages)