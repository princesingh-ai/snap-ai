import httpx

from fastapi import FastAPI, Request
from fastapi.responses import Response, StreamingResponse
from app.config.settings import settings


app = FastAPI()

BACKEND_URL = (f"http://{settings.backend_host}:{settings.backend_port}")
LLAMA_URL = (f"http://{settings.llama_host}:{settings.llama_port}")


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def gateway(request: Request, path: str):

    if path in {
        "v1/chat/completions",
        "v1/chat/completions/control"}:
        target = f"{BACKEND_URL}/{path}"
    else:
        target = f"{LLAMA_URL}/{path}"

    body = await request.body()

    headers = {
        key: value
        for key, value in request.headers.items()
        if key.lower() not in {"host", "content-length"}}

    # Streaming chat requests go through FastAPI
    if path == "v1/chat/completions" and request.method == "POST":

        client = httpx.AsyncClient(timeout=None)

        upstream = await client.send(
            client.build_request(request.method, target, headers=headers, content=body) ,stream=True)

        async def stream():
            try:
                async for chunk in upstream.aiter_raw():
                    yield chunk
            finally:
                await upstream.aclose()
                await client.aclose()

        response_headers = {
            key: value
            for key, value in upstream.headers.items()
            if key.lower()
            not in {"content-length", "transfer-encoding", "connection", "content-encoding"}}

        return StreamingResponse(
            stream(),
            status_code=upstream.status_code,
            headers=response_headers,
            media_type=upstream.headers.get("content-type"))

    # All other requests go directly to llama.cpp
    async with httpx.AsyncClient(timeout=None) as client:

        response = await client.request(request.method, target, headers=headers, content=body)

    response_headers = {
        key: value
        for key, value in response.headers.items()
        if key.lower()
        not in {"content-length", "transfer-encoding", "connection", "content-encoding"}}

    return Response(content=response.content, status_code=response.status_code, headers=response_headers, media_type=response.headers.get("content-type"))
