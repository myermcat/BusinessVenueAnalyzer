"""Alias package to maintain backward compatibility after renaming.

Re-exports everything from the original ``proximity`` package so existing code
continues to work while clients migrate to the new path.
"""
from importlib import import_module as _imp

# Re-export submodules lazily
def __getattr__(name):
    if name in {"models", "services"}:
        return _imp(f"{__name__}.{name}")
    raise AttributeError(name)

__all__ = ["models", "services"]
