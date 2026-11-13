"""Measure baseline memory consumption and record to docs/memory_baseline.md."""

import os
from datetime import datetime, timezone

import psutil


def get_process_memory_mb(process: psutil.Process) -> float:
    return process.memory_info().rss / (1024 * 1024)


def main() -> None:
    process = psutil.Process(os.getpid())
    virtual_mem = psutil.virtual_memory()

    total_ram_mb = virtual_mem.total / (1024 * 1024)
    available_ram_mb = virtual_mem.available / (1024 * 1024)
    percent_used = virtual_mem.percent

    # Baseline RSS at start
    rss_start = get_process_memory_mb(process)

    # After importing sqlite3
    import sqlite3  # noqa: F401
    rss_after_sqlite = get_process_memory_mb(process)

    # After importing pydantic
    import pydantic  # noqa: F401
    rss_after_pydantic = get_process_memory_mb(process)

    # After importing fastapi
    import fastapi  # noqa: F401
    rss_after_fastapi = get_process_memory_mb(process)

    now_iso = datetime.now(timezone.utc).isoformat()

    report = f"""# Memory Baseline Report

- **Timestamp (UTC)**: {now_iso}
- **Operating System**: {os.name} ({psutil.sys.platform})

## System Memory

- **Total System RAM**: {total_ram_mb:.2f} MB ({total_ram_mb / 1024:.2f} GB)
- **Available System RAM**: {available_ram_mb:.2f} MB ({available_ram_mb / 1024:.2f} GB)
- **RAM Usage**: {percent_used:.1f}%

## Process RSS (Resident Set Size)

| Stage | Process RSS (MB) | Delta from Start (MB) |
|---|---|---|
| Process Start (baseline) | {rss_start:.2f} | 0.00 |
| After `import sqlite3` | {rss_after_sqlite:.2f} | {rss_after_sqlite - rss_start:+.2f} |
| After `import pydantic` | {rss_after_pydantic:.2f} | {rss_after_pydantic - rss_start:+.2f} |
| After `import fastapi` | {rss_after_fastapi:.2f} | {rss_after_fastapi - rss_start:+.2f} |
"""

    docs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs")
    output_path = os.path.join(docs_dir, "memory_baseline.md")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(report)


if __name__ == "__main__":
    main()
