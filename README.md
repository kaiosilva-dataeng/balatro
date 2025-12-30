# Balatro Soul Farm Automation

This tool automates the process of farming "The Soul" card in the game Balatro. It scans the screen for specific game elements (tags, cards) and interacts with them to maximize the chances of finding the soul card.

## Features

- **Automated Farming**: Automatically starts new games, skips tags, and buys cards.
- **Log Processing**: Tracks statistics like running time, found tags, and souls found.
- **Interruptible**: Can be paused or stopped with keyboard shortcuts.

## Installation

This project is managed with [`uv`](https://github.com/astral-sh/uv). Ensure you have it installed.

```bash
# Clone the repository (if applicable) or navigate to the project directory
uv tool install https://github.com/kaiosilva-dataeng/balatro.git
```

## Usage

To start the automation, use `uvx`:

```bash
uvx soul_farm
```

## Controls

Once the script is running, the following keyboard shortcuts are available:

- `P`: **Start/Resume** the automation loop.
- `M`: **Pause** the loop (finishes the current cycle first).
- `L`: **Exit** the application completely.

## Calibration & Configuration

The tool runs out-of-the-box for **1920x1080** resolution.

If your screen resolution is different, the tool will automatically trigger a **calibration mode** on first run. Follow the on-screen instructions to capture the coordinates for skip buttons and menu interactions.

This configuration is saved to `src/balatro/config.json`.

## Logs & Statistics

Logs are saved to your home directory:
`~/.balatro/logs/` (e.g., `C:\Users\Username\.balatro\logs\`)

When you exit the application (using `L` or by letting it finish), it will parse the current session's log and display statistics such as:

- Total Running Time
- Total Double Tags Found
- Total Charm Tags Found
- Total Souls Opened
- Efficiency metrics (Charms per Soul, Souls per Hour)

## Structure

- `src/balatro/soul_farm.py`: Core automation logic (screen scanning, mouse interaction).
- `src/balatro/process_log.py`: Log analysis and reporting.
- `src/balatro/main.py`: Entry point ensuring proper execution flow.
