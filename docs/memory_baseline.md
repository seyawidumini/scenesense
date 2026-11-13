# Memory Baseline Report

- **Timestamp (UTC)**: 2026-11-13T11:50:20.301685+00:00
- **Operating System**: nt (win32)

## System Memory

- **Total System RAM**: 7835.82 MB (7.65 GB)
- **Available System RAM**: 685.11 MB (0.67 GB)
- **RAM Usage**: 91.3%

## Process RSS (Resident Set Size)

| Stage | Process RSS (MB) | Delta from Start (MB) |
|---|---|---|
| Process Start (baseline) | 18.23 | 0.00 |
| After `import sqlite3` | 18.52 | +0.29 |
| After `import pydantic` | 23.57 | +5.34 |
| After `import fastapi` | 43.69 | +25.46 |

## Measurement Run: 2026-11-13T12:10:17.852361+00:00

- **Open Applications / Note**: Baseline environment (Antigravity IDE, Google Chrome, Windows Explorer, background system services)

### System Memory (at start)
- **Total System RAM**: 7835.82 MB (7.65 GB)
- **Available System RAM at Start**: 815.43 MB (0.80 GB)
- **RAM Usage at Start**: 89.6%

### Process RSS (Import Stages)
| Stage | Process RSS (MB) | Delta from Start (MB) |
|---|---|---|
| Process Start (baseline) | 26.18 | 0.00 |
| After `import sqlite3` | 26.43 | +0.25 |
| After `import pydantic` | 29.46 | +3.27 |
| After `import fastapi` | 44.26 | +18.07 |

### Uvicorn Server RSS (GET /health)
- **Uvicorn Worker RSS while Serving**: 52.32 MB
- **Total Uvicorn Process Tree RSS**: 56.42 MB
- **Lifecycle**: Started uvicorn server process, served one GET /health request (200 OK), then stopped process cleanly.
