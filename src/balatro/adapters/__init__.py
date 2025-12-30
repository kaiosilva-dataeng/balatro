# Adapters layer - external I/O abstractions
from .config import JsonConfigRepository
from .input import DirectInputAdapter
from .ports import AbstractConfigPort, AbstractInputPort, AbstractScreenPort
from .screen import PyAutoGuiScreenAdapter

__all__ = [
    # Ports (interfaces)
    'AbstractScreenPort',
    'AbstractInputPort',
    'AbstractConfigPort',
    # Real implementations
    'PyAutoGuiScreenAdapter',
    'DirectInputAdapter',
    'JsonConfigRepository',
]
