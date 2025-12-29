import cv2
import numpy as np
import pyautogui
import time
import keyboard
from pathlib import Path
from soul_farm import data, ASSETS_DIR

def run_full_screen_scan():
    print(f"\n[{time.strftime('%H:%M:%S')}] 🔍 SCANNING FULL SCREEN FOR ASSETS (OpenCV)...")
    print("This might take a few seconds per asset.")
    
    # Capture screen once
    screenshot = pyautogui.screenshot()
    haystack = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

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
                center_x = pt[0] + w//2
                center_y = pt[1] + h//2
                
                icon = "✅" if confidence >= 0.9 else "⚠️" if confidence >= 0.8 else "❓"
                print(f"     {icon} Conf: {confidence:.4f} | Pos: ({pt[0]}, {pt[1]}) | Center: ({center_x}, {center_y})")
                
                if found_count >= 10: # Limit output
                    print("     ... (limiting to top 10 matches)")
                    break

            if found_count == 0:
                 print(f"  ❌ {name} NOT found (max confidence < {threshold})")

        except Exception as e:
            print(f"  ⚠️ Error scanning {name}: {repr(e)}")
    print("------------------------------------------------")

def test_assets():
    print("=== INTERACTIVE ASSET DEBUGGER ===")
    print("Press 'F' to SCAN FULL SCREEN (Find correct coordinates).")
    print("Press 'Q' to quit.")
    
    while True:
        if keyboard.is_pressed('f'):
            run_full_screen_scan()
            time.sleep(0.5)
        elif keyboard.is_pressed('q'):
            print("Exiting...")
            break
        time.sleep(0.1)


if __name__ == "__main__":
    test_assets()
