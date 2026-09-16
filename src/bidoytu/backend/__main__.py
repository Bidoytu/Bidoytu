"""Versioned JSON-lines RPC over private stdin/stdout pipes; no HTTP control port."""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

from .service import ApplicationService

MAX_MESSAGE = 2 * 1024 * 1024


async def serve(data_dir: Path, ca_dir: Path | None = None):
    # Reserve original stdout for protocol frames; dependency prints go to stderr.
    output = sys.stdout
    sys.stdout = sys.stderr
    lock = asyncio.Lock()

    async def emit(message):
        encoded = json.dumps(message, ensure_ascii=True, separators=(",", ":")) + "\n"
        async with lock:
            await asyncio.to_thread(write, encoded)

    def write(encoded):
        output.write(encoded)
        output.flush()

    service = ApplicationService(data_dir, emit, ca_dir=ca_dir)
    await service.open()
    await emit({"event": "ready", "data": service.state()})
    tasks: set[asyncio.Task] = set()

    async def handle(message):
        request_id = message.get("id") if isinstance(message, dict) else None
        try:
            if not isinstance(message, dict) or not isinstance(message.get("method"), str) or not isinstance(message.get("params", {}), dict):
                raise ValueError("Invalid RPC envelope")
            result = await service.dispatch(message["method"], message.get("params", {}))
            await emit({"id": request_id, "result": result})
        except Exception as exc:
            await emit({"id": request_id, "error": {"message": str(exc) or type(exc).__name__}})

    try:
        while True:
            line = await asyncio.to_thread(sys.stdin.buffer.readline, MAX_MESSAGE + 1)
            if not line:
                break
            if len(line) > MAX_MESSAGE:
                await emit({"event": "fatal", "data": "RPC message exceeds 2 MiB"})
                break
            try:
                message = json.loads(line)
            except (ValueError, UnicodeDecodeError):
                await emit({"id": None, "error": {"message": "Invalid JSON"}})
                continue
            if len(tasks) >= 32:
                await emit({"id": message.get("id") if isinstance(message, dict) else None,
                            "error": {"message": "Backend busy; retry shortly"}})
                continue
            task = asyncio.create_task(handle(message))
            tasks.add(task)
            task.add_done_callback(tasks.discard)
    finally:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        await service.close()


def main():
    parser = argparse.ArgumentParser(description="Bidoytu headless desktop backend")
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--ca-dir", type=Path)
    args = parser.parse_args()
    asyncio.run(serve(args.data_dir, args.ca_dir))


if __name__ == "__main__":
    main()
