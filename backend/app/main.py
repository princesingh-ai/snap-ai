from fastapi import FastAPI
from pydantic import BaseModel

from app.inference.llama_client import LlamaClient

app = FastAPI(title="snap", description="A simple API for interacting with the LLaMA model", version="1.0.0")

llama = LlamaClient(base_url="http://localhost:8080")

MODEL_NAME = "ggml-org/gemma-4-E2B-it-GGUF:Q8_0"

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
    response = await llama.chat(model=MODEL_NAME, messages=messages)
    return response