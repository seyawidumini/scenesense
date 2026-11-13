# Architectural Decisions (ADR)

## ADR-001: Python-only Backend for MVP
- **Decision**: Use Python 3.10+ (FastAPI + Pydantic) for the complete backend rather than ASP.NET or multi-language services.
- **Context**: Rapid development of NLP/evaluation pipelines, native data-science tooling, and lower memory overhead compared to running mixed runtimes concurrently.
- **Consequences**: Fast prototyping, clean integration with pytest and future ML/evaluation packages.

## ADR-002: No LangGraph Unless Demonstrated Need
- **Decision**: Build deterministic game state orchestration directly in pure Python; do not introduce LangGraph or complex agent frameworks at this stage.
- **Context**: State machines for character knowledge and game turns must remain deterministic, fully debuggable, and transparent. Framework overhead and opacity add unnecessary complexity on low-spec hardware.

## ADR-003: SQLite + JSON for World Truth and Knowledge
- **Decision**: Store structured world state, character claims, clues, and knowledge bases using lightweight SQLite and JSON schemas.
- **Context**: Avoids running dedicated external database servers (e.g. Postgres, MongoDB) and operates with negligible memory consumption.

## ADR-004: Provider-Independent LLM Interface with Mock and Disk Cache
- **Decision**: Define a minimal `LLMClient` protocol accompanied by `MockLLMClient` and disk-based `CachingLLMClient`.
- **Context**: Enables reproducible testing, deterministic regression benchmarks, and offline development without requiring API keys or incurring costs.

## ADR-005: Scripted Demo Mode (No API Keys Required)
- **Decision**: Ensure the core game loop, evaluation harness, and demo flows can execute entirely using scripted/mock responses without network access or secret credentials.

## ADR-006: No Local LLMs on Constrained Hardware
- **Decision**: Strictly prohibit installing or running local LLM weights (Ollama, PyTorch, Transformers, GGUF) on this machine (Intel Core i3, 8 GB RAM with ~1 GB free).
- **Context**: System memory is constrained and lacking a dedicated GPU; local model execution would cause severe swap thrashing and out-of-memory crashes.
