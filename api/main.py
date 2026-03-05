"""Backward-compatible API entrypoint.

Prefer `services.api.main`.
"""

from services.api.main import app, health, score  # noqa: F401
