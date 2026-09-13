from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from fastapi import Depends
from fastapi import HTTPException

from app.inference.llama_client import LlamaClient
from app.services.model_services import ModelService
from app.services.task_analyzer import TaskAnalyzer
from app.services.model_router import ModelRouter
from app.services.org_data_analyzer import OrgDataAnalyzer
from app.input.detector import has_document_input
from app.config.settings import settings
from app.config.loader import load_task_analyzer

from app.mcp.server import mcp

from app.auth.jwt import create_access_token
from app.auth.users import authenticate_user, add_user
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.auth.permissions import require_permission
from app.services.mcp_client import MCPClient
from app.auth.dependencies import get_current_access_token
from app.auth.rbac import Role, is_allowed

add_user(
    user_id="admin-001",
    username="admin",
    password="admin-password",
    role=Role.ADMIN,
)

add_user(
    user_id="engineering-001",
    username="engineering",
    password="engineering-password",
    role=Role.ENGINEERING,
)

add_user(
    user_id="finance-001",
    username="finance",
    password="finance-password",
    role=Role.FINANCE,
)

mcp_app = mcp.http_app(path="/")

app = FastAPI(
    title="snap",
    description="A simple API for interacting with the LLaMA model",
    version="1.0.0",
    lifespan=mcp_app.lifespan,
)

app.mount("/mcp", mcp_app)

llama = LlamaClient(base_url=f"http://{settings.llama_host}:{settings.llama_port}")
model_service = ModelService(llama_client=llama)

task_analyzer_config = load_task_analyzer()
task_analyzer = TaskAnalyzer(llama_client=llama, model=task_analyzer_config["name"])

org_data_analyzer = OrgDataAnalyzer(llama_client=llama, model=task_analyzer_config["name"])

model_router = ModelRouter()

mcp_client = MCPClient(base_url="http://127.0.0.1:8000/mcp/")

class Message(BaseModel):
    """A message in the chat conversation, consisting of a role and content."""
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: list[Message]

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str

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
@app.post("/v1/chat/completions")
async def chat_completions(request: dict, current_user: User = Depends(get_current_user), access_token: str = Depends(get_current_access_token)):

    messages = request.get("messages", [])
    print("[DEBUG] FULL REQUEST:")
    print(request)

    if has_document_input(messages):
        model_key = model_router.route_document_image()

        print("[DEBUG] DOCUMENT/IMAGE INPUT DETECTED")
        print(f"[DEBUG] MODEL: {model_key}")

    else:
        org_data = await org_data_analyzer.analyze(messages)

        print(f"[DEBUG] ORG DATA: {org_data}")

        if org_data["requires_org_data"]:
            resource_type = org_data["resource_type"]
            search_query = org_data["search_query"]

            if not is_allowed(
                current_user.role,
                resource_type,
                "read",
            ):
                raise HTTPException(
                    status_code=403,
                    detail=(
                        f"Role '{current_user.role.value}' is not allowed "
                        f"to access '{resource_type}' resources."
                    ),
                )

            org_context = await mcp_client.retrieve_context(
                query=search_query,
                resource_type=resource_type,
                access_token=access_token,
            )

            if org_context:
                messages = [
                    {
                        "role": "system",
                        "content": (
                            "The following information comes from authorized "
                            "internal organizational data. Use it to answer the "
                            "user's request. Do not invent information that is "
                            "not present in the supplied context.\n\n"
                            f"{org_context}"
                        ),
                    },
                    *messages,
                ]

            print("[DEBUG] MCP CONTEXT:")
            print(org_context)

        task = await task_analyzer.analyze(messages)
        model_key = model_router.route(task)

        print(f"[DEBUG] TASK: {task}")
        print(f"[DEBUG] MODEL: {model_key}")

    if request.get("stream", False):

        async def generate():

            async for chunk in model_service.chat_stream(
                model_key=model_key,
                messages=messages,
                request_body=request,
            ):
                yield chunk

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    return await model_service.chat(
        model_key=model_key,
        messages=messages,
    )

@app.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    user = authenticate_user(
        request.username,
        request.password,
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password.",
        )

    token = create_access_token(user)

    return LoginResponse(
        access_token=token,
        token_type="bearer",
    )

@app.get("/auth/me")
async def auth_me(current_user: User = Depends(get_current_user)):
    return {
        "user_id": current_user.user_id,
        "username": current_user.username,
        "role": current_user.role.value,
    }

@app.get("/auth/test-finance")
async def test_finance_access(
    current_user: User = Depends(
        require_permission("finance", "read")
    ),
):
    return {
        "message": "Finance access granted.",
        "user": current_user.username,
        "role": current_user.role.value,
    }