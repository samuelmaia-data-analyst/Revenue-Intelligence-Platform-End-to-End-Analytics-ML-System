from __future__ import annotations

import os

import uvicorn


def main() -> None:
    host = os.getenv("RIP_API_HOST", "0.0.0.0")
    port = int(os.getenv("RIP_API_PORT", "8000"))
    reload_enabled = os.getenv("RIP_API_RELOAD", "false").strip().lower() == "true"
    uvicorn.run("services.api.main:app", host=host, port=port, reload=reload_enabled)
