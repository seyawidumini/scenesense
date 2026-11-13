# SceneSense AI

Playable AI detective mystery and reproducible evaluation framework (SceneBench).

## Project Summary
SceneSense investigates whether enforcing character knowledge boundaries at the data layer (filtered retrieval + structured knowledge + output validation) reduces secret leakage and unsupported claims compared with prompt-only characters.

**Core Principle**: The LLM is a voice, not the brain. Authored claims and world truth live in JSON and SQLite; the engine decides what may be disclosed; the LLM only phrases it.

## Status
**Milestone 0: Skeleton, Tooling, and Memory Baseline Complete**

## Setup & Running Tests (Windows PowerShell)

### Prerequisites
- Python 3.10+ installed
- Virtual environment created outside OneDrive (e.g., `C:\venvs\scenesense`)

### 1. Activate Virtual Environment
```powershell
C:\venvs\scenesense\Scripts\Activate.ps1
```

### 2. Install Project in Editable Mode with Dev Dependencies
```powershell
pip install -e ".[dev]"
```

### 3. Run Memory Baseline Measurement
```powershell
python scripts/measure_memory.py
```

### 4. Run Test Suite
```powershell
pytest
```

### 5. Run API Server (Development)
```powershell
uvicorn api.main:app --port 8000
```
Health endpoint verification:
```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

## Limitations
*(None recorded for Milestone 0)*
