import time

import cv2
import keyboard
import numpy as np
import pyautogui

from balatro.soul_farm import ASSETS_DIR, CONFIG, data


def run_scan(region=None, label="FULL SCREEN"):
    print(f"\n[{time.strftime('%H:%M:%S')}] 🔍 SCANNING {label} FOR ASSETS (OpenCV)...")
    if region:
        print(f"Region: {region}")

    # Capture screen once
    screenshot = pyautogui.screenshot(region=region)
    haystack = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # Offset to convert back to global screen coordinates
    off_x, off_y = (region[0], region[1]) if region else (0, 0)

    for name, _ in data.items():
        img_path = str(ASSETS_DIR / name)
        needle = cv2.imread(img_path)

        if needle is None:
            print(f"  ⚠️ Error: Could not load {name}")
            continue

        try:
            result = cv2.matchTemplate(haystack, needle, cv2.TM_CCOEFF_NORMED)
            # Find all matches above 0.6 to see potential candidates
            threshold = data[name].get("confiance", 0.6)
            loc = np.where(result >= threshold)

            # Zip and sort by confidence (descending)
            matches = list(zip(*loc[::-1]))
            # Sort by confidence
            matches.sort(key=lambda pt: result[pt[1], pt[0]], reverse=True)

            found_count = 0
            # Simple non-max suppression (very basic: skip if close to previous)
            processed_points = []

            print(f"  Checking {name}...")

            for pt in matches:
                confidence = result[pt[1], pt[0]]

                # Basic dedup (if within 10 pixels of another printed match)
                is_duplicate = False
                for pp in processed_points:
                    if abs(pt[0] - pp[0]) < 10 and abs(pt[1] - pp[1]) < 10:
                        is_duplicate = True
                        break

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

                icon = "✅" if confidence >= 0.9 else "⚠️" if confidence >= threshold else "❓"
                print(
                    f"     {icon} Conf: {confidence:.4f} | Local: ({pt[0]}, {pt[1]}) | Global Center: ({global_x}, {global_y})"
                )

                if found_count >= 10:  # Limit output
                    print("     ... (limiting to top 10 matches)")
                    break

            if found_count == 0:
                print(f"  ❌ {name} NOT found (max confidence < {threshold})")

        except Exception as e:
            print(f"  ⚠️ Error scanning {name}: {repr(e)}")
    print("------------------------------------------------")


def test_assets():
    print("=== INTERACTIVE ASSET DEBUGGER ===")
    print("Press 'F' to SCAN FULL SCREEN.")
    print("Press 'S' to SCAN SKIP SLOTS ROI.")
    print("Press 'T' to SCAN THE SOUL ROI.")
    print("Press 'Q' to quit.")

    while True:
        if keyboard.is_pressed("f"):
            run_scan(region=None, label="FULL SCREEN")
            time.sleep(0.5)
        elif keyboard.is_pressed("s"):
            r1 = CONFIG.get("skip_slots_1")
            run_scan(region=r1, label="SKIP SLOT 1 ROI")
            
            time.sleep(0.5)
            
            r2 = CONFIG.get("skip_slots_2")
            run_scan(region=r2, label="SKIP SLOT 2 ROI")
            
            time.sleep(0.5)
        elif keyboard.is_pressed("t"):
            roi_config = CONFIG.get("the_soul")
            rois = roi_config if isinstance(roi_config, list) else [roi_config]
            
            for i, r in enumerate(rois):
                run_scan(region=r, label=f"THE SOUL ROI #{i+1}")
                if keyboard.is_pressed("q"): break # Allow aborting loop
            
            time.sleep(0.5)
        elif keyboard.is_pressed("q"):
            print("Exiting...")
            break
        time.sleep(0.1)


if __name__ == "__main__":
    test_assets()
