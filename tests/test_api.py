"""Portable HTTP serving checks that do not download model weights."""

from __future__ import annotations

from types import SimpleNamespace

import api
import pytest
from fastapi.testclient import TestClient


class StubGenerator:
    def __init__(self) -> None:
        self.calls: list[tuple[str, int, float]] = []

    def generate(self, prompt, *, max_new_tokens, temperature):
        self.calls.append((prompt, max_new_tokens, temperature))
        return SimpleNamespace(response="Inspect git status before committing.")


def test_generate_uses_shared_bounded_inference(monkeypatch):
    monkeypatch.delenv("TINYDEVASSIST_API_KEY", raising=False)
    generator = StubGenerator()
    client = TestClient(api.create_api(generator))
    response = client.post(
        "/generate", json={"prompt": "  What changed?  ", "temperature": 0, "max_new_tokens": 64}
    )
    assert response.status_code == 200
    assert response.json() == {"response": "Inspect git status before committing."}
    assert generator.calls == [("What changed?", 64, 0.0)]


def test_health_checks_configuration_without_loading_weights(monkeypatch):
    monkeypatch.delenv("HF_MODEL_REPO", raising=False)
    monkeypatch.delenv("TINYDEVASSIST_ADAPTER_PATH", raising=False)
    client = TestClient(api.create_api())
    assert client.get("/healthz").status_code == 503
    monkeypatch.setenv("HF_MODEL_REPO", "namespace/adapter")
    assert client.get("/healthz").json() == {"status": "configured"}


def test_optional_api_key_protects_generation(monkeypatch):
    monkeypatch.setenv("TINYDEVASSIST_API_KEY", "a-test-secret")
    generator = StubGenerator()
    client = TestClient(api.create_api(generator))
    assert client.post("/generate", json={"prompt": "Git?"}).status_code == 401
    assert (
        client.post(
            "/generate", json={"prompt": "Git?"}, headers={"X-API-Key": "wrong"}
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/generate", json={"prompt": "Git?"}, headers={"X-API-Key": "a-test-secret"}
        ).status_code
        == 200
    )
    assert len(generator.calls) == 1


def test_model_failure_returns_generic_service_error(monkeypatch):
    monkeypatch.delenv("TINYDEVASSIST_API_KEY", raising=False)

    class BrokenGenerator:
        def generate(self, prompt, *, max_new_tokens, temperature):
            raise RuntimeError("internal model path must stay private")

    response = TestClient(api.create_api(BrokenGenerator())).post(
        "/generate", json={"prompt": "Git?"}
    )
    assert response.status_code == 503
    assert response.json() == {"detail": "model unavailable"}


@pytest.mark.parametrize(
    "payload",
    [
        {"prompt": " "},
        {"prompt": "Git?", "max_new_tokens": 512},
        {"prompt": "Git?", "temperature": 1.5},
        {"prompt": "Git?", "unexpected": "value"},
    ],
)
def test_invalid_requests_never_reach_model(monkeypatch, payload):
    monkeypatch.delenv("TINYDEVASSIST_API_KEY", raising=False)
    generator = StubGenerator()
    client = TestClient(api.create_api(generator))
    assert client.post("/generate", json=payload).status_code == 422
    assert generator.calls == []


def test_port_follows_platform_environment(monkeypatch):
    monkeypatch.delenv("PORT", raising=False)
    assert api.configured_port() == 8080
    monkeypatch.setenv("PORT", "10000")
    assert api.configured_port() == 10000
    monkeypatch.setenv("PORT", "not-a-port")
    with pytest.raises(ValueError, match="PORT"):
        api.configured_port()
    monkeypatch.setenv("PORT", "70000")
    with pytest.raises(ValueError, match="PORT"):
        api.configured_port()
