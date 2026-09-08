from fastapi import FastAPI, Request
from fastapi.responses import Response, StreamingResponse
from app.config.settings import settings
import httpx


app = FastAPI(title="snap reverse proxy")


LLAMA_URL = (f"http://{settings.llama_host}:{settings.llama_port}")
FASTAPI_URL = (f"http://{settings.backend_host}:{settings.backend_port}")


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):

    print("[PROXY] Chat request → FastAPI")

    body = await request.body()

    async def stream():
        async with httpx.AsyncClient(timeout=None) as client:

            async with client.stream(
                "POST",
                f"{FASTAPI_URL}/v1/chat/completions",
                content=body,
                headers={
                    "Content-Type": request.headers.get(
                        "content-type",
                        "application/json",
                    ),
                },
            ) as response:

                async for chunk in response.aiter_bytes():
                    yield chunk

    return StreamingResponse(
        stream(),
        status_code=200,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/props")
async def props():

    print("[PROXY] /props → llama.cpp")

    async with httpx.AsyncClient(timeout=30) as client:

        response = await client.get(
            f"{LLAMA_URL}/props"
        )

    return Response(
        content=response.content,
        status_code=response.status_code,
        media_type=response.headers.get(
            "content-type",
            "application/json",
        ),
    )


@app.get("/v1/models")
async def models():

    print("[PROXY] /v1/models → llama.cpp")

    async with httpx.AsyncClient(timeout=30) as client:

        response = await client.get(
            f"{LLAMA_URL}/v1/models"
        )

    return Response(
        content=response.content,
        status_code=response.status_code,
        media_type=response.headers.get(
            "content-type",
            "application/json",
        ),
    )



@app.get("/models/sse")
async def models_sse(request: Request):

    print("[PROXY] /models/sse → llama.cpp")

    async def stream():

        async with httpx.AsyncClient(timeout=None) as client:

            async with client.stream(
                "GET",
                f"{LLAMA_URL}/models/sse",
                headers={
                    key: value
                    for key, value in request.headers.items()
                    if key.lower() != "host"
                },
            ) as response:

                async for chunk in response.aiter_bytes():

                    if await request.is_disconnected():
                        break

                    yield chunk

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

@app.api_route(
    "/{path:path}",
    methods=[
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "PATCH",
        "OPTIONS",
    ],
)
async def proxy_to_llama(request: Request, path: str):

    print(f"[PROXY] /{path} → llama.cpp")

    body = await request.body()

    async with httpx.AsyncClient(timeout=30) as client:

        response = await client.request(
            method=request.method,
            url=f"{LLAMA_URL}/{path}",
            content=body,
            headers={
                key: value
                for key, value in request.headers.items()
                if key.lower() != "host"
            },
        )

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers={
            key: value
            for key, value in response.headers.items()
            if key.lower()
            not in {
                "content-encoding",
                "transfer-encoding",
                "content-length",
            }
        },
    )