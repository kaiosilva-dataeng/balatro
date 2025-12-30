
import pytest
from balatro.process_log import parse_log_statistics

def test_parse_log_statistics_basic():
    log_content = """2025-12-29 21:00:00,000 - INFO - Balatro Automation Ready.
2025-12-29 21:00:01,000 - INFO - ACTION: New Game Started
2025-12-29 21:00:02,000 - INFO - DECISION: Skip for double and charm
2025-12-29 21:00:05,000 - INFO - ACTION: New Game Started
2025-12-29 21:00:06,000 - INFO - DECISION: Skip for charm (slot 2)
2025-12-29 21:00:07,000 - INFO - Selecting SOUL card at (500, 500)
2025-12-29 21:00:10,000 - INFO - End of test run
"""
    stats = parse_log_statistics(log_content)
    
    assert stats["new_game_count"] == 2
    assert stats["total_doubles"] == 1
    assert stats["total_charms"] == 2 # 1 from double+charm, 1 from charm (slot 2)
    assert stats["total_souls"] == 1
    assert stats["duration_seconds"] == 10.0
    assert stats["run_time_str"] == "0h 0m 10s"

def test_parse_log_statistics_empty():
    log_content = ""
    stats = parse_log_statistics(log_content)
    
    assert stats["new_game_count"] == 0
    assert stats["total_doubles"] == 0
    assert stats["duration_seconds"] == 0
    assert stats["run_time_str"] == "0h 0m 0s"

def test_parse_log_statistics_decisions():
    log_content = """2025-12-29 21:00:00,000 - Start
2025-12-29 21:00:01,000 - DECISION: Skip for double and charm
2025-12-29 21:00:02,000 - DECISION: Skip for charm and charm
2025-12-29 21:00:03,000 - DECISION: Skip for charm (slot 1)
2025-12-29 21:00:04,000 - DECISION: Skip for charm (slot 2)
"""
    stats = parse_log_statistics(log_content)
    
    assert stats["total_doubles"] == 1
    # 1 (double+charm) + 2 (charm+charm) + 1 (slot 1) + 1 (slot 2) = 5
    assert stats["total_charms"] == 5 

def test_parse_log_statistics_metrics():
    # 1 hour duration, 2 resets
    log_content = """2025-12-29 21:00:00,000 - Start
2025-12-29 21:00:00,000 - ACTION: New Game Started
2025-12-29 21:30:00,000 - ACTION: New Game Started
2025-12-29 22:00:00,000 - End
"""
    stats = parse_log_statistics(log_content)
    
    assert stats["duration_seconds"] == 3600.0
    assert stats["new_game_count"] == 2
    assert stats["resets_per_hour"] == 2.0
    assert stats["avg_reset_time"] == 1800.0
