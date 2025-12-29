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
    
    # Timestamps to calculate running time
    timestamps = []
    
    # Regex patterns
    time_pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})"
    double_pattern = r"Found double.png"
    charm_pattern = r"Found charm.png"
    soul_pattern = r"Found the_soul.png"

    lines = log_text.strip().split('\n')
    
    for line in lines:
        # Extract time for running time calculation
        time_match = re.search(time_pattern, line)
        if time_match:
            timestamps.append(datetime.strptime(time_match.group(1), "%Y-%m-%d %H:%M:%S,%f"))
        
        # Count occurrences (handles multiple finds in one line)
        total_doubles += len(re.findall(double_pattern, line))
        total_charms += len(re.findall(charm_pattern, line))
        total_souls += len(re.findall(soul_pattern, line))

    # Calculate Running Time (Total span across all sessions in log)
    if timestamps:
        duration = max(timestamps) - min(timestamps)
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        run_time_str = f"{hours}h {minutes}m {seconds}s"
    else:
        run_time_str = "0h 0m 0s"

    # Display Results
    print("### Balatro Automation Statistics ###")
    print(f"Total Running Time:    {run_time_str}")
    print("-" * 35)
    print(f"Total Double Tags:     {total_doubles}")
    print(f"Total Charm Tags:      {total_charms}")
    print("-" * 35)
    
    # Summary of tags found
    print(f"Detailed Quantitatives:")
    print(f"* Charms: {total_charms*total_doubles}")
    print(f"Total Souls Opened:    {total_souls}")
    print(f"* Charms per Soul: {(total_charms*total_doubles)/total_souls}")
    print(f"Souls per hour: {total_souls/(duration.seconds/3600)}")
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
        process_balatro_logs(latest_log_file.read_text(encoding='utf-8'))
    else:
        print("No log files found.")
