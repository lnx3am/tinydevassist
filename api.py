"""Portable CPU HTTP service for the published TinyDevAssist adapter."""

from __future__ import annotations

import hmac
import os
from threading import Lock
from typing import Any

import app as core_app
import uvicorn
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field


class GenerateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prompt: str = Field(min_length=1, max_length=2000)
    temperature: float = Field(default=0.0, ge=0.0, le=1.0)
    max_new_tokens: int = Field(default=96, ge=16, le=256)


def configured_port() -> int:
    """Use the container platform's port, with a local default."""
    value = os.environ.get("PORT", "8080")
    try:
        port = int(value)
    except ValueError as exc:
        raise ValueError("PORT must be an integer between 1 and 65535") from exc
    if not 1 <= port <= 65535:
        raise ValueError("PORT must be an integer between 1 and 65535")
    return port


def create_api(generator: Any = None) -> FastAPI:
    """Build an API without loading model weights at import time."""
    service = FastAPI(title="TinyDevAssist API", version="1.0.0", redoc_url=None)
    generation_lock = Lock()

    @service.get("/healthz")
    def health() -> dict[str, str]:
        if generator is None and not (
            os.environ.get("HF_MODEL_REPO") or os.environ.get("TINYDEVASSIST_ADAPTER_PATH")
        ):
            raise HTTPException(status_code=503, detail="adapter is not configured")
        return {"status": "configured"}

    @service.post("/generate")
    def generate(
        request: GenerateRequest, api_key: str | None = Header(default=None, alias="X-API-Key")
    ) -> dict[str, str]:
        expected_key = os.environ.get("TINYDEVASSIST_API_KEY")
        if expected_key and (api_key is None or not hmac.compare_digest(api_key, expected_key)):
            raise HTTPException(status_code=401, detail="invalid API key")
        try:
            with generation_lock:
                answer = core_app.respond(
                    request.prompt,
                    request.temperature,
                    request.max_new_tokens,
                    generator=generator,
                )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except (OSError, RuntimeError) as exc:
            raise HTTPException(status_code=503, detail="model unavailable") from exc
        return {"response": answer}

    return service


service = create_api()

if __name__ == "__main__":
    uvicorn.run(service, host="0.0.0.0", port=configured_port(), workers=1)
