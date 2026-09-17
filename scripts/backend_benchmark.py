"""Reproducible local storage benchmark; emits measurements, not performance claims."""
from __future__ import annotations

import asyncio
import json
import statistics
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from bidoytu.backend.service import ApplicationService


async def main():
    with tempfile.TemporaryDirectory() as directory:
        async def emit(event):
            pass
        service = ApplicationService(Path(directory), emit)
        await service.open()
        try:
            def seed():
                service.storage.repo._conn.executemany(
                    "INSERT INTO flows(flow_id,method,host,path,status_code,response_body_inline,response_body_size) VALUES(?,?,?,?,?,?,?)",
                    ((str(i), "GET", f"api-{i % 20}.test", f"/v1/items/{i}", 200, b"x" * 4096, 4096) for i in range(10000)))
                service.storage.repo._conn.commit()
            await service.storage.call(seed)
            samples = []
            for _ in range(40):
                start = time.perf_counter()
                page = await service.dispatch("history.list", {"limit": 100})
                samples.append((time.perf_counter() - start) * 1000)
            report = {"rows": 10000, "stored_body_bytes": 40960000, "page_rows": len(page["items"]),
                      "page_payload_bytes": len(json.dumps(page).encode()),
                      "page_latency_median_ms": round(statistics.median(samples), 2),
                      "page_latency_p95_ms": round(sorted(samples)[37], 2),
                      "python": sys.version.split()[0]}
            target = Path("test-results/backend-benchmark.json")
            target.parent.mkdir(exist_ok=True)
            target.write_text(json.dumps(report, indent=2), encoding="utf-8")
            print(json.dumps(report, indent=2))
        finally:
            await service.close()


if __name__ == "__main__":
    asyncio.run(main())
