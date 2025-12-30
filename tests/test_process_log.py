"""Tests for log parsing statistics."""

from balatro.process_log import parse_log_statistics

# Expected values for test cases
EXPECTED_BASIC_GAMES = 2
EXPECTED_BASIC_DOUBLES = 1
EXPECTED_BASIC_CHARMS = 2  # 1 from double+charm, 1 from charm (slot 2)
EXPECTED_BASIC_SOULS = 1
EXPECTED_BASIC_DURATION = 10.0

EXPECTED_DECISIONS_DOUBLES = 1
EXPECTED_DECISIONS_CHARMS = 5  # 1 + 2 + 1 + 1 = 5

EXPECTED_METRICS_DURATION = 3600.0  # 1 hour
EXPECTED_METRICS_GAMES = 2
EXPECTED_METRICS_RESETS_PER_HOUR = 2.0
EXPECTED_METRICS_AVG_RESET = 1800.0  # 30 minutes


def test_parse_log_statistics_basic():
    """Test basic log parsing with typical log entries."""
    log_content = """2025-12-29 21:00:00,000 - INFO - Balatro Automation Ready.
2025-12-29 21:00:01,000 - INFO - ACTION: New Game Started
2025-12-29 21:00:02,000 - INFO - DECISION: Skip for double and charm
2025-12-29 21:00:05,000 - INFO - ACTION: New Game Started
2025-12-29 21:00:06,000 - INFO - DECISION: Skip for charm (slot 2)
2025-12-29 21:00:07,000 - INFO - Selecting SOUL card at (500, 500)
2025-12-29 21:00:10,000 - INFO - End of test run
"""
    stats = parse_log_statistics(log_content)

    assert stats['new_game_count'] == EXPECTED_BASIC_GAMES
    assert stats['total_doubles'] == EXPECTED_BASIC_DOUBLES
    assert stats['total_charms'] == EXPECTED_BASIC_CHARMS
    assert stats['total_souls'] == EXPECTED_BASIC_SOULS
    assert stats['duration_seconds'] == EXPECTED_BASIC_DURATION
    assert stats['run_time_str'] == '0h 0m 10s'


def test_parse_log_statistics_empty():
    """Test parsing an empty log file."""
    log_content = ''
    stats = parse_log_statistics(log_content)

    assert stats['new_game_count'] == 0
    assert stats['total_doubles'] == 0
    assert stats['duration_seconds'] == 0
    assert stats['run_time_str'] == '0h 0m 0s'


def test_parse_log_statistics_decisions():
    """Test correct counting of all decision types."""
    log_content = """2025-12-29 21:00:00,000 - Start
2025-12-29 21:00:01,000 - DECISION: Skip for double and charm
2025-12-29 21:00:02,000 - DECISION: Skip for charm and charm
2025-12-29 21:00:03,000 - DECISION: Skip for charm (slot 1)
2025-12-29 21:00:04,000 - DECISION: Skip for charm (slot 2)
"""
    stats = parse_log_statistics(log_content)

    assert stats['total_doubles'] == EXPECTED_DECISIONS_DOUBLES
    assert stats['total_charms'] == EXPECTED_DECISIONS_CHARMS


def test_parse_log_statistics_metrics():
    """Test derived metrics calculation (1 hour duration, 2 resets)."""
    log_content = """2025-12-29 21:00:00,000 - Start
2025-12-29 21:00:00,000 - ACTION: New Game Started
2025-12-29 21:30:00,000 - ACTION: New Game Started
2025-12-29 22:00:00,000 - End
"""
    stats = parse_log_statistics(log_content)

    assert stats['duration_seconds'] == EXPECTED_METRICS_DURATION
    assert stats['new_game_count'] == EXPECTED_METRICS_GAMES
    assert stats['resets_per_hour'] == EXPECTED_METRICS_RESETS_PER_HOUR
    assert stats['avg_reset_time'] == EXPECTED_METRICS_AVG_RESET
