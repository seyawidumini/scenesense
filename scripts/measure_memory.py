"""Measure baseline memory consumption and record to docs/memory_baseline.md."""

import argparse
import contextlib
import os
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone

import psutil


def get_process_memory_mb(process: psutil.Process) -> float:
    return process.memory_info().rss / (1024 * 1024)


def measure_uvicorn_process_rss(port: int = 8000) -> dict[str, float]:
    """Start uvicorn in a separate process, measure RSS while serving /health, then stop it."""
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "api.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        str(port),
        "--log-level",
        "error",
    ]
    proc = subprocess.Popen(cmd)
    parent_ps = psutil.Process(proc.pid)

    # Wait briefly for server startup
    time.sleep(1.2)
    worker_rss_mb = 0.0
    total_rss_mb = 0.0

    try:
        url = f"http://127.0.0.1:{port}/health"
        with urllib.request.urlopen(url) as response:
            if response.status != 200:
                raise RuntimeError(f"Unexpected status code: {response.status}")

            procs = [parent_ps] + parent_ps.children(recursive=True)
            worker_proc = max(procs, key=lambda p: p.memory_info().rss)
            worker_rss_mb = worker_proc.memory_info().rss / (1024 * 1024)
            total_rss_mb = sum(p.memory_info().rss for p in procs) / (1024 * 1024)
    finally:
        for child in parent_ps.children(recursive=True):
            with contextlib.suppress(psutil.NoSuchProcess, psutil.AccessDenied):
                child.kill()
        proc.terminate()
        proc.wait()

    return {"worker_rss_mb": worker_rss_mb, "total_rss_mb": total_rss_mb}


def main() -> None:
    parser = argparse.ArgumentParser(description="Measure SceneSense memory baseline.")
    parser.add_argument(
        "--note",
        type=str,
        default="",
        help="Context note describing open applications or environment state.",
    )
    parser.add_argument(
        "--append",
        action="store_true",
        default=True,
        help="Append to docs/memory_baseline.md instead of overwriting.",
    )
    args = parser.parse_args()

    # (1) Available system RAM at start
    virtual_mem_start = psutil.virtual_memory()
    total_ram_mb = virtual_mem_start.total / (1024 * 1024)
    available_ram_start_mb = virtual_mem_start.available / (1024 * 1024)
    percent_used_start = virtual_mem_start.percent

    # Measure current process RSS stages
    current_proc = psutil.Process(os.getpid())
    rss_start = get_process_memory_mb(current_proc)

    import sqlite3  # noqa: F401
    rss_after_sqlite = get_process_memory_mb(current_proc)

    import pydantic  # noqa: F401
    rss_after_pydantic = get_process_memory_mb(current_proc)

    import fastapi  # noqa: F401
    rss_after_fastapi = get_process_memory_mb(current_proc)

    # (2) Measure RSS of uvicorn process while serving GET /health
    uvicorn_metrics = measure_uvicorn_process_rss()

    now_iso = datetime.now(timezone.utc).isoformat()
    note_line = f"\n- **Open Applications / Note**: {args.note}\n" if args.note else ""

    section = f"""
## Measurement Run: {now_iso}
{note_line}
### System Memory (at start)
- **Total System RAM**: {total_ram_mb:.2f} MB ({total_ram_mb / 1024:.2f} GB)
- **Available System RAM at Start**: {available_ram_start_mb:.2f} MB ({available_ram_start_mb / 1024:.2f} GB)
- **RAM Usage at Start**: {percent_used_start:.1f}%

### Process RSS (Import Stages)
| Stage | Process RSS (MB) | Delta from Start (MB) |
|---|---|---|
| Process Start (baseline) | {rss_start:.2f} | 0.00 |
| After `import sqlite3` | {rss_after_sqlite:.2f} | {rss_after_sqlite - rss_start:+.2f} |
| After `import pydantic` | {rss_after_pydantic:.2f} | {rss_after_pydantic - rss_start:+.2f} |
| After `import fastapi` | {rss_after_fastapi:.2f} | {rss_after_fastapi - rss_start:+.2f} |

### Uvicorn Server RSS (GET /health)
- **Uvicorn Worker RSS while Serving**: {uvicorn_metrics['worker_rss_mb']:.2f} MB
- **Total Uvicorn Process Tree RSS**: {uvicorn_metrics['total_rss_mb']:.2f} MB
- **Lifecycle**: Started uvicorn server process, served one GET /health request (200 OK), then stopped process cleanly.
"""

    docs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs")
    output_path = os.path.join(docs_dir, "memory_baseline.md")

    if args.append and os.path.exists(output_path):
        with open(output_path, "a", encoding="utf-8") as f:
            f.write(section)
    else:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# Memory Baseline Report\n{section}")

    print(section)


if __name__ == "__main__":
    main()
