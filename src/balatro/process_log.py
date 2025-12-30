"""
Backward compatibility module for process_log.

This module re-exports the analytics functions from the service layer
to maintain compatibility with existing imports.
"""

from .service_layer.analytics import (
    display_statistics,
    parse_log_statistics,
    process_balatro_logs,
)

__all__ = [
    'parse_log_statistics',
    'display_statistics',
    'process_balatro_logs',
]
