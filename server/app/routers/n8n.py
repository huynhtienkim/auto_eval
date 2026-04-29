"""Forward requests to upstream n8n."""
from __future__ import annotations

from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Request, status
from starlette.responses import Response

from app.config import N8N_UPSTREAM

router = APIRouter(prefix="/api/n8n", tags=["n8n"])


@router.api_route(
    "/{full_path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
)
async def n8n_proxy(full_path: str, request: Request):
    """
    Forward browser calls to n8n so the page only talks to this API (same origin → no n8n CORS).
    Set N8N_UPSTREAM_URL in .env to your n8n root.
    """
    if not N8N_UPSTREAM:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Set N8N_UPSTREAM_URL in server/.env to your n8n base URL, then restart uvicorn.",
        )
    tail = full_path.lstrip("/")
    target = f"{N8N_UPSTREAM}/{tail}" if tail else N8N_UPSTREAM

    if request.method == "OPTIONS":
        return Response(status_code=204)

    body = await request.body()
    fwd: dict[str, str] = {}
    for k, v in request.headers.items():
        lk = k.lower()
        if lk in ("content-type", "accept", "authorization"):
            fwd[k] = v

    timeout = httpx.Timeout(300.0, connect=20.0)
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=False) as client:
            kwargs: dict[str, Any] = {"method": request.method, "url": target, "headers": fwd}
            if body:
                kwargs["content"] = body
            r = await client.request(**kwargs)
    except httpx.RequestError as e:
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY,
            f"Cannot reach n8n at {target!s}: {e!s}",
        ) from e

    ct = r.headers.get("content-type") or "application/octet-stream"
    media = ct.split(";")[0].strip()
    return Response(content=r.content, status_code=r.status_code, media_type=media)
