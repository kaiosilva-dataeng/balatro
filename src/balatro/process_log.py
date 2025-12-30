"""
Module for processing Balatro automation logs.
"""

import re
from datetime import datetime
from pathlib import Path


def process_balatro_logs(log_text: str) -> None:
    """
    Parses the Balatro log text to extract and display statistics about the automation run.

    Args:
        log_text (str): The content of the log file.
    """
    # Data structures
    total_doubles = 0
    total_charms = 0
    total_souls = 0
    new_game_count = 0

    # Timestamps to calculate running time
    timestamps = []

    # Regex patterns
    time_pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})"
    
    # Decision Patterns (Actions taken)
    decision_double_charm = r"DECISION: Skip for double and charm"
    decision_charm_charm = r"DECISION: Skip for charm and charm"
    decision_charm_slot1 = r"DECISION: Skip for charm \(slot 1\)"
    decision_charm_slot2 = r"DECISION: Skip for charm \(slot 2\)"
    
    # Soul Action (Actually clicking it)
    soul_action_pattern = r"Selecting SOUL card"
    
    # New Game Action
    new_game_pattern = r"ACTION: New Game Started"

    lines = log_text.strip().split("\n")

    for line in lines:
        # Extract time for running time calculation
        time_match = re.search(time_pattern, line)
        if time_match:
            try:
                timestamps.append(
                    datetime.strptime(time_match.group(1), "%Y-%m-%d %H:%M:%S,%f")
                )
            except ValueError:
                pass

        # Count Actions based on Decisions
        if re.search(decision_double_charm, line):
            total_doubles += 1
            total_charms += 1
        elif re.search(decision_charm_charm, line):
            total_charms += 2
        elif re.search(decision_charm_slot1, line):
            total_charms += 1
        elif re.search(decision_charm_slot2, line):
            total_charms += 1
            
        # Count Souls (Actions)
        total_souls += len(re.findall(soul_action_pattern, line))
        
        # Count New Games
        new_game_count += len(re.findall(new_game_pattern, line))

    # Calculate Running Time
    duration_seconds = 0
    if timestamps:
        duration = max(timestamps) - min(timestamps)
        duration_seconds = duration.total_seconds()
        hours, remainder = divmod(int(duration_seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        run_time_str = f"{hours}h {minutes}m {seconds}s"
    else:
        run_time_str = "0h 0m 0s"

    # Derived Metrics
    resets_per_hour = 0.0
    if duration_seconds > 0:
        resets_per_hour = new_game_count / (duration_seconds / 3600)

    avg_reset_time = 0.0
    if new_game_count > 0 and duration_seconds > 0:
         avg_reset_time = duration_seconds / new_game_count

    souls_per_hour = 0.0
    if duration_seconds > 0:
        souls_per_hour = total_souls / (duration_seconds / 3600)

    # Simplified Display
    print("### Balatro Automation Statistics ###")
    print(f"Total Running Time:    {run_time_str}")
    print("-" * 35)
    print(f"Resets (New Games):    {new_game_count}")
    print(f"Resets per Hour:       {resets_per_hour:.2f}")
    print(f"Avg Time per Reset:    {avg_reset_time:.2f}s")
    print("-" * 35)
    print(f"Decisions Executed:")
    print(f"  Doubles Taken:       {total_doubles}")
    print(f"  Charms Taken:        {total_charms}")
    print(f"  Souls Clicked:       {total_souls}")
    print(f"Souls per Hour:        {souls_per_hour:.2f}")
    print("-" * 35)


if __name__ == "__main__":
    LOGS_DIR = Path.home() / ".balatro" / "logs"

    if not LOGS_DIR.exists():
        print(f"No log directory found at {LOGS_DIR}")
        exit()

    files = list(LOGS_DIR.glob("*.log"))

    if files:
        latest_log_file = max(files, key=lambda p: p.stat().st_mtime)
        print(f"Processing latest log: {latest_log_file.name}")
        content = latest_log_file.read_text(encoding="utf-8")
        if not content.strip():
            print("Log file is empty.")
        else:
            process_balatro_logs(content)
    else:
        print("No log files found.")
