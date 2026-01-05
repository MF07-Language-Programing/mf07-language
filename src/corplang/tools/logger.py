"""Compatibility shim exposing `get_logger` for older imports.

Some modules import `src.corplang.tools.logger.get_logger`. Provide a thin
wrapper delegating to `src.corplang.core.config.get_logger` to avoid
duplicate implementations.
"""
from src.corplang.core.config import get_logger as _get_logger


def get_logger(name: str):
    return _get_logger(name)
