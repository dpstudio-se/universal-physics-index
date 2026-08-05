"""Odysseus AI Protocol Bridge Package."""

from .core import (
    OdysseusIntentExecutor,
    OdysseusToolRegistry,
    execute_odysseus_tool,
    get_odysseus_tools_manifest,
)

__version__ = "0.1.0"

__all__ = [
    "OdysseusToolRegistry",
    "OdysseusIntentExecutor",
    "get_odysseus_tools_manifest",
    "execute_odysseus_tool",
    "__version__",
]
