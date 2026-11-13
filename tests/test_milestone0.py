from fastapi.testclient import TestClient

from api.main import app
from llm.client import CachingLLMClient, MockLLMClient


def test_mock_llm_client_determinism():
    client = MockLLMClient()
    resp1 = client.generate("Who was in the parlor?", model="mock-model-v1", temperature=0.0)
    resp2 = client.generate("Who was in the parlor?", model="mock-model-v1", temperature=0.0)

    assert resp1.text == resp2.text
    assert resp1.input_tokens == resp2.input_tokens
    assert resp1.output_tokens == resp2.output_tokens
    assert resp1.cached is False
    assert resp2.cached is False
    assert client.call_count == 2

    # Different prompt produces different response text
    resp3 = client.generate("Who was in the conservatory?", model="mock-model-v1")
    assert resp3.text != resp1.text
    assert client.call_count == 3


def test_caching_llm_client_hit_miss(tmp_path):
    mock_client = MockLLMClient()
    caching_client = CachingLLMClient(wrapped_client=mock_client, cache_dir=str(tmp_path))

    # First call: cache miss, calls wrapped client
    resp1 = caching_client.generate(
        "Find the candlestick",
        model="mock-v1",
        temperature=0.2,
        max_tokens=64,
        system="You are a detective.",
    )
    assert resp1.cached is False
    assert mock_client.call_count == 1

    # Second call with identical arguments: cache hit, wrapped client NOT called
    resp2 = caching_client.generate(
        "Find the candlestick",
        model="mock-v1",
        temperature=0.2,
        max_tokens=64,
        system="You are a detective.",
    )
    assert resp2.cached is True
    assert resp2.text == resp1.text
    assert resp2.input_tokens == resp1.input_tokens
    assert resp2.output_tokens == resp1.output_tokens
    assert mock_client.call_count == 1  # Still 1!


def test_caching_llm_client_key_changes_on_parameter_change(tmp_path):
    mock_client = MockLLMClient()
    caching_client = CachingLLMClient(wrapped_client=mock_client, cache_dir=str(tmp_path))

    # Base call
    caching_client.generate("Inspect the study", model="mock-v1", temperature=0.0, max_tokens=100)
    assert mock_client.call_count == 1

    # Vary prompt
    caching_client.generate("Inspect the library", model="mock-v1", temperature=0.0, max_tokens=100)
    assert mock_client.call_count == 2

    # Vary model
    caching_client.generate("Inspect the study", model="mock-v2", temperature=0.0, max_tokens=100)
    assert mock_client.call_count == 3

    # Vary temperature
    caching_client.generate("Inspect the study", model="mock-v1", temperature=0.7, max_tokens=100)
    assert mock_client.call_count == 4

    # Vary max_tokens
    caching_client.generate("Inspect the study", model="mock-v1", temperature=0.0, max_tokens=200)
    assert mock_client.call_count == 5

    # Vary system prompt
    caching_client.generate(
        "Inspect the study",
        model="mock-v1",
        temperature=0.0,
        max_tokens=100,
        system="System prompt active",
    )
    assert mock_client.call_count == 6

    # Repeating any of the above should be cached and not increase call_count
    cached_resp = caching_client.generate(
        "Inspect the study",
        model="mock-v1",
        temperature=0.7,
        max_tokens=100,
    )
    assert cached_resp.cached is True
    assert mock_client.call_count == 6


def test_api_health_endpoint():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
