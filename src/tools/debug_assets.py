"""
Debug tool for testing asset detection.
"""

import time
from pathlib import Path

import cv2
import keyboard
import numpy as np
import pyautogui

from balatro.adapters.config import JsonConfigRepository

# Constants
DEDUP_THRESHOLD = 10
HIGH_CONFIDENCE = 0.9
MAX_MATCHES = 10

BASE_DIR = Path(__file__).resolve().parent.parent / 'balatro'
ASSETS_DIR = BASE_DIR / 'assets'
CONFIG_FILE = BASE_DIR / 'config.json'

# Load config
config_repo = JsonConfigRepository(CONFIG_FILE)
profile = config_repo.load_profile(config_repo.get_current_profile_name())

# Asset data
ASSET_THRESHOLDS = {
    'the_soul.png': 0.65,
    'double.png': 0.90,
    'charm.png': 0.90,
}


def run_scan(region=None, label='FULL SCREEN'):
    """Scan a region for all known assets."""
    timestamp = time.strftime('%H:%M:%S')
    print(f'\n[{timestamp}] 🔍 SCANNING {label} FOR ASSETS (OpenCV)...')
    if region:
        print(f'Region: {region}')

    # Capture screen once
    screenshot = pyautogui.screenshot(region=region)
    haystack = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # Offset to convert back to global screen coordinates
    off_x, off_y = (region[0], region[1]) if region else (0, 0)

    for name, threshold in ASSET_THRESHOLDS.items():
        img_path = str(ASSETS_DIR / name)
        needle = cv2.imread(img_path)

        if needle is None:
            print(f'  ⚠️ Error: Could not load {name}')
            continue

        try:
            result = cv2.matchTemplate(haystack, needle, cv2.TM_CCOEFF_NORMED)
            loc = np.where(result >= threshold)

            # Zip and sort by confidence (descending)
            matches = list(zip(*loc[::-1]))
            matches.sort(key=lambda pt: result[pt[1], pt[0]], reverse=True)

            found_count = 0
            # Simple non-max suppression
            processed_points = []

            print(f'  Checking {name}...')

            for pt in matches:
                confidence = result[pt[1], pt[0]]

                # Basic dedup (within DEDUP_THRESHOLD pixels)
                is_duplicate = any(
                    abs(pt[0] - pp[0]) < DEDUP_THRESHOLD
                    and abs(pt[1] - pp[1]) < DEDUP_THRESHOLD
                    for pp in processed_points
                )

                if is_duplicate:
                    continue

                processed_points.append(pt)
                found_count += 1

                # Get dimensions
                h, w = needle.shape[:2]
                local_center_x = pt[0] + w // 2
                local_center_y = pt[1] + h // 2

                # Global coordinates
                global_x = local_center_x + off_x
                global_y = local_center_y + off_y

                if confidence >= HIGH_CONFIDENCE:
                    icon = '✅'
                elif confidence >= threshold:
                    icon = '⚠️'
                else:
                    icon = '❓'

                print(
                    f'     {icon} Conf: {confidence:.4f} | '
                    f'Local: ({pt[0]}, {pt[1]}) | '
                    f'Global: ({global_x}, {global_y})'
                )

                if found_count >= MAX_MATCHES:
                    print(f'     ... (limiting to top {MAX_MATCHES} matches)')
                    break

            if found_count == 0:
                print(f'  ❌ {name} NOT found (max confidence < {threshold})')

        except Exception as e:
            print(f'  ⚠️ Error scanning {name}: {repr(e)}')
    print('------------------------------------------------')


def test_assets():
    """Interactive asset debugger."""
    print('=== INTERACTIVE ASSET DEBUGGER ===')
    print("Press 'F' to SCAN FULL SCREEN.")
    print("Press 'S' to SCAN SKIP SLOTS ROI.")
    print("Press 'T' to SCAN THE SOUL ROI.")
    print("Press 'Q' to quit.")

    while True:
        if keyboard.is_pressed('f'):
            run_scan(region=None, label='FULL SCREEN')
            time.sleep(0.5)
        elif keyboard.is_pressed('s'):
            rois = profile.get_rois('skip_slots_1')
            for roi in rois:
                run_scan(region=roi.to_tuple(), label='SKIP SLOT 1 ROI')

            time.sleep(0.5)

            rois = profile.get_rois('skip_slots_2')
            for roi in rois:
                run_scan(region=roi.to_tuple(), label='SKIP SLOT 2 ROI')

            time.sleep(0.5)
        elif keyboard.is_pressed('t'):
            rois = profile.get_rois('the_soul')

            for i, roi in enumerate(rois):
                run_scan(region=roi.to_tuple(), label=f'THE SOUL ROI #{i + 1}')
                if keyboard.is_pressed('q'):
                    break

            time.sleep(0.5)
        elif keyboard.is_pressed('q'):
            print('Exiting...')
            break
        time.sleep(0.1)


if __name__ == '__main__':
    test_assets()
