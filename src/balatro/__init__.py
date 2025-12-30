"""
Balatro Soul Farm Automation.

A modular automation tool for farming The Soul card in Balatro.
Architecture inspired by "Cosmic Python" (Architecture Patterns with Python).

Layers:
- domain: Pure business logic (models, decisions, exceptions)
- service_layer: Use cases and orchestration (farming, scanning, analytics)
- adapters: External I/O abstractions (screen, input, config)
- entrypoints: Application entry points (CLI)
"""

from .domain.decisions import FarmingDecision, decide_farming_action

# Re-export domain models
from .domain.model import (
    Coordinates,
    GameState,
    ProfileConfig,
    Region,
    ScanResult,
)

# Re-export main services for programmatic use
from .service_layer.analytics import AnalyticsService
from .service_layer.farming import FarmingService
from .service_layer.scanning import ScanService

__all__ = [
    # Services
    'FarmingService',
    'ScanService',
    'AnalyticsService',
    # Domain models
    'Coordinates',
    'Region',
    'ScanResult',
    'GameState',
    'ProfileConfig',
    'FarmingDecision',
    'decide_farming_action',
]

__version__ = '0.2.0'
