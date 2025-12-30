
import sys
import os

# Add src to path so we can import the module
sys.path.append(os.path.join(os.getcwd(), 'src'))

from balatro.process_log import process_balatro_logs

log_content = """2025-12-29 21:00:00,000 - INFO - Balatro Automation Ready.
2025-12-29 21:00:01,000 - INFO - ACTION: New Game Started
2025-12-29 21:00:02,000 - INFO - DECISION: Skip for double and charm
2025-12-29 21:00:05,000 - INFO - ACTION: New Game Started
2025-12-29 21:00:06,000 - INFO - DECISION: Skip for charm (slot 2)
2025-12-29 21:00:07,000 - INFO - Selecting SOUL card at (500, 500)
2025-12-29 21:00:10,000 - INFO - End of test run
"""

print("Running test with DECISION based logs...")
process_balatro_logs(log_content)
