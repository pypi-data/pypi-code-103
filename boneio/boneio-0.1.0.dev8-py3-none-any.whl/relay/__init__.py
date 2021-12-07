"""Relay module."""
from .gpio import GpioRelay
from .mcp import MCPRelay

__all__ = ["MCPRelay", "GpioRelay"]
