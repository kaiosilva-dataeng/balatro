# 🃏 Balatro Soul Farm Automation

![CI](https://github.com/kaiosilva-dataeng/balatro/actions/workflows/ci.yml/badge.svg)
![Coverage](./coverage.svg)

Automated farming tool for "The Soul" card in Balatro. Uses image recognition to scan the screen for game elements and interacts with them to maximize soul card farming efficiency.

## Features

- **Automated Farming**: Automatically starts new games, skips tags, and buys cards.
- **Log Processing**: Tracks statistics like running time, found tags, and souls found.
- **Interruptible**: Can be paused or stopped with keyboard shortcuts.
- **Modular Architecture**: Clean separation of concerns for easy testing and maintenance.

## Installation

Requires [`uv`](https://github.com/astral-sh/uv):

```bash
uv tool install https://github.com/kaiosilva-dataeng/balatro.git
```

## Usage

```bash
uvx soul_farm
```

## Controls

- `P`: **Start/Resume** the automation loop
- `M`: **Pause** the loop
- `L`: **Exit** the application

## Configuration

Runs out-of-the-box for **1920x1080** resolution. Configuration saved to `src/balatro/config.json`.

## Logs & Statistics

Logs saved to `~/.balatro/logs/`. On exit, displays:
- Total Running Time
- Double/Charm Tags Found
- Souls Opened
- Efficiency metrics (Souls per Hour)

## Architecture

Built following [Cosmic Python](https://www.cosmicpython.com/) patterns:

```
src/balatro/
├── domain/           # Pure business logic (models, decisions, exceptions)
│   ├── model.py      # Coordinates, Region, ScanResult, GameState, ProfileConfig
│   ├── decisions.py  # FarmingDecision logic
│   └── exceptions.py # Custom exceptions
│
├── service_layer/    # Use cases and orchestration
│   ├── farming.py    # FarmingService - main automation loop
│   ├── scanning.py   # ScanService - screen scanning
│   └── analytics.py  # AnalyticsService - log parsing
│
├── adapters/         # External I/O abstractions
│   ├── ports.py      # Abstract interfaces (Protocols)
│   ├── screen.py     # PyAutoGUI/OpenCV screen adapter
│   ├── input.py      # DirectInput keyboard/mouse adapter
│   └── config.py     # JSON config repository
│
├── entrypoints/      # Application entry points
│   └── cli.py        # CLI entry point
│
└── assets/           # Image assets for detection
```

### Key Benefits

| Benefit | How |
|---------|-----|
| **Testability** | Fake adapters allow unit testing without screen/keyboard |
| **Maintainability** | Each layer has single responsibility |
| **Debuggability** | Clear boundaries isolate issues |
| **Evolvability** | Add new adapters without changing domain |

## Development

```bash
# Install dev dependencies
uv sync --dev

# Run tests
uv run pytest tests/ -v

# Run the automation
uv run soul_farm
```
