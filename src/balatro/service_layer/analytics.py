"""
Analytics service for processing automation logs.

Parses log files and calculates statistics for farming sessions.
"""

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class FarmingStatistics:
    """Value object containing farming session statistics."""

    total_doubles: int = 0
    total_charms: int = 0
    total_souls: int = 0
    new_game_count: int = 0
    duration_seconds: float = 0.0
    run_time_str: str = '0h 0m 0s'
    resets_per_hour: float = 0.0
    avg_reset_time: float = 0.0
    souls_per_hour: float = 0.0


class AnalyticsService:
    """
    Service for analyzing automation logs and generating statistics.
    """

    # Regex patterns for log parsing
    TIME_PATTERN = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})'
    DECISION_DOUBLE_CHARM = r'DECISION: Skip for double and charm'
    DECISION_CHARM_CHARM = r'DECISION: Skip for charm and charm'
    DECISION_CHARM_SLOT1 = r'DECISION: Skip for charm \(slot 1\)'
    DECISION_CHARM_SLOT2 = r'DECISION: Skip for charm \(slot 2\)'
    SOUL_ACTION = r'Selecting SOUL card'
    NEW_GAME_ACTION = r'ACTION: New Game Started'

    def parse_log(self, log_text: str) -> FarmingStatistics:
        """
        Parse log text and calculate statistics.

        Args:
            log_text: Content of the log file.

        Returns:
            FarmingStatistics object with calculated metrics.
        """
        total_doubles = 0
        total_charms = 0
        total_souls = 0
        new_game_count = 0
        timestamps: list[datetime] = []

        lines = log_text.strip().split('\n')

        for line in lines:
            # Extract timestamp
            time_match = re.search(self.TIME_PATTERN, line)
            if time_match:
                try:
                    timestamps.append(
                        datetime.strptime(
                            time_match.group(1), '%Y-%m-%d %H:%M:%S,%f'
                        )
                    )
                except ValueError:
                    pass

            # Count decisions
            if re.search(self.DECISION_DOUBLE_CHARM, line):
                total_doubles += 1
                total_charms += 1
            elif re.search(self.DECISION_CHARM_CHARM, line):
                total_charms += 2
            elif re.search(self.DECISION_CHARM_SLOT1, line):
                total_charms += 1
            elif re.search(self.DECISION_CHARM_SLOT2, line):
                total_charms += 1

            # Count souls
            total_souls += len(re.findall(self.SOUL_ACTION, line))

            # Count new games
            new_game_count += len(re.findall(self.NEW_GAME_ACTION, line))

        # Calculate duration
        duration_seconds = 0.0
        run_time_str = '0h 0m 0s'
        if timestamps:
            duration = max(timestamps) - min(timestamps)
            duration_seconds = duration.total_seconds()
            hours, remainder = divmod(int(duration_seconds), 3600)
            minutes, seconds = divmod(remainder, 60)
            run_time_str = f'{hours}h {minutes}m {seconds}s'

        # Calculate derived metrics
        resets_per_hour = 0.0
        avg_reset_time = 0.0
        souls_per_hour = 0.0

        if duration_seconds > 0:
            resets_per_hour = new_game_count / (duration_seconds / 3600)
            souls_per_hour = total_souls / (duration_seconds / 3600)

            if new_game_count > 0:
                avg_reset_time = duration_seconds / new_game_count

        return FarmingStatistics(
            total_doubles=total_doubles,
            total_charms=total_charms,
            total_souls=total_souls,
            new_game_count=new_game_count,
            duration_seconds=duration_seconds,
            run_time_str=run_time_str,
            resets_per_hour=resets_per_hour,
            avg_reset_time=avg_reset_time,
            souls_per_hour=souls_per_hour,
        )

    def display_statistics(self, stats: FarmingStatistics) -> None:
        """
        Display statistics to stdout.

        Args:
            stats: The statistics to display.
        """
        print('\n### Balatro Automation Statistics ###')
        print(f'Total Running Time:    {stats.run_time_str}')
        print('-' * 40)
        print(f'Resets (New Games):    {stats.new_game_count}')
        print(f'Resets per Hour:       {stats.resets_per_hour:.2f}')
        print(f'Avg Time per Reset:    {stats.avg_reset_time:.2f}s')
        print('-' * 40)
        print('Decisions Executed:')
        print(f'  Doubles Taken:       {stats.total_doubles}')
        print(f'  Charms Taken:        {stats.total_charms}')
        print(f'  Souls Clicked:       {stats.total_souls}')
        print(f'Souls per Hour:        {stats.souls_per_hour:.2f}')
        print('-' * 40)

    def process_log_file(self, log_path: Path) -> Optional[FarmingStatistics]:
        """
        Process a log file and display statistics.

        Args:
            log_path: Path to the log file.

        Returns:
            Statistics if file exists and has content, None otherwise.
        """
        if not log_path.exists():
            print(f'Log file not found: {log_path}')
            return None

        content = log_path.read_text(encoding='utf-8')
        if not content.strip():
            print('Log file is empty.')
            return None

        stats = self.parse_log(content)
        self.display_statistics(stats)
        return stats


# Backward compatibility functions
def parse_log_statistics(log_text: str) -> dict:
    """
    Parse log text and return statistics as a dictionary.

    Maintained for backward compatibility with existing tests.
    """
    service = AnalyticsService()
    stats = service.parse_log(log_text)
    return {
        'total_doubles': stats.total_doubles,
        'total_charms': stats.total_charms,
        'total_souls': stats.total_souls,
        'new_game_count': stats.new_game_count,
        'duration_seconds': stats.duration_seconds,
        'run_time_str': stats.run_time_str,
        'resets_per_hour': stats.resets_per_hour,
        'avg_reset_time': stats.avg_reset_time,
        'souls_per_hour': stats.souls_per_hour,
    }


def display_statistics(stats: dict) -> None:
    """
    Display statistics from a dictionary.

    Maintained for backward compatibility.
    """
    service = AnalyticsService()
    farming_stats = FarmingStatistics(**stats)
    service.display_statistics(farming_stats)


def process_balatro_logs(log_text: str) -> None:
    """
    Process log text and display statistics.

    Maintained for backward compatibility.
    """
    service = AnalyticsService()
    stats = service.parse_log(log_text)
    service.display_statistics(stats)
