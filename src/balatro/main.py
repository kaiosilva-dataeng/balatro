
import cv2
import numpy as np
import pyautogui
import pydirectinput
import keyboard
from PIL import Image
import time
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Setup paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ASSETS_DIR = BASE_DIR / "assets"


data = {
    "the_soul.png": {
        "pos": [(620, 666), (795, 666), (970, 666), (1145, 666), (1320, 666)],
        "width": 148,
        "height": 220,

        "confiance": 0.8,
    },
    "double.png": {
        "pos": [(567, 810)],
        "width": 68,
        "height": 68,
        "confiance": 0.9,
    },
    "charm.png": {
        "pos": [(567, 810), (919, 870)],
        "width": 68,
        "height": 68,
        "confiance": 0.9,
    },
    "ethereal.png": {
        "pos": [(567, 810), (919, 870)],
        "width": 68,
        "height": 68,
        "confiance": 0.9,
    },
}


def scan_for_image(img_ref):
    """
    Scans the entire screen for the given image reference.
    Returns a list of found matches: [{'pos': (x, y), 'conf': float, 'slot': 1|2}]
    """
    img_path = str(ASSETS_DIR / img_ref)
    needle = cv2.imread(img_path)
    
    if needle is None:
        logging.error(f"Could not load image: {img_ref}")
        return []

    try:
        # Capture screen
        screenshot = pyautogui.screenshot()
        haystack = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        result = cv2.matchTemplate(haystack, needle, cv2.TM_CCOEFF_NORMED)
        
        # Get threshold from data or default
        threshold = data[img_ref].get("confiance", 0.8)
        
        loc = np.where(result >= threshold)
        matches = list(zip(*loc[::-1]))
        
        # Sort by confidence
        matches.sort(key=lambda pt: result[pt[1], pt[0]], reverse=True)
        
        found_objects = []
        processed_points = []
        
        for pt in matches:
            # Dedup close matches
            if any(abs(pt[0] - pp[0]) < 10 and abs(pt[1] - pp[1]) < 10 for pp in processed_points):
                continue
                
            processed_points.append(pt)
            confidence = result[pt[1], pt[0]]
            
            # Calculate center
            h, w = needle.shape[:2]
            center_x = pt[0] + w//2
            center_y = pt[1] + h//2
            
            # Determine slot (Split screen at X=750)
            slot = 1 if pt[0] < 750 else 2
            
            logging.info(f"Found {img_ref} | Slot {slot} | Conf: {confidence:.2f}")
            found_objects.append({'pos': (center_x, center_y), 'conf': float(confidence), 'slot': slot})
            
        return found_objects

    except Exception as e:
        logging.error(f"Error scanning for {img_ref}: {e}")
        return []


def arcana():
    time.sleep(5)
    
    # Scan specifically for soul card inside the pack
    soul_matches = scan_for_image("soul.png")
    
    if soul_matches:
        # Take the best match
        best = soul_matches[0]
        centre = best['pos']
        
        logging.info(f"Selecting SOUL card at {centre}")
        pydirectinput.moveTo(centre[0], centre[1])
        pydirectinput.click()
        time.sleep(1.5)
        
        # Click "Use" button (offset relative to card center)
        # Using fixed offset from original code logic
        # Original: (data["soul.png"]["height"] // 2) - 10
        # height is 220, so offset is 110 - 10 = 100
        pydirectinput.moveTo(centre[0], centre[1] + 100)
        pydirectinput.click()
        time.sleep(0.5)


def arcana1():
    pydirectinput.moveTo(715, 850)
    pydirectinput.click()
    arcana()


def arcana2():
    pydirectinput.moveTo(715, 850)
    pydirectinput.click()
    time.sleep(0.2)
    pydirectinput.moveTo(1070, 850)
    pydirectinput.click()
    arcana()


def arcana12():
    arcana1()
    pydirectinput.moveTo(1335, 975)
    pydirectinput.click()
    time.sleep(0.5)
    pydirectinput.moveTo(1070, 850)
    pydirectinput.click()
    arcana()


def nouvelle_partie():
    pydirectinput.press("esc")
    time.sleep(0.5)
    pydirectinput.moveTo(955, 355)
    pydirectinput.click()
    time.sleep(0.5)
    pydirectinput.moveTo(955, 830)
    pydirectinput.click()
    time.sleep(0.5)


def balatro():
    print("Balatro Automation Ready.")
    print("Press 'P' to start/resume.")
    print("Press 'M' to pause loop.")
    print("Press 'L' to exit completely.")
    while True:
        try:
            if keyboard.is_pressed("p"):
                while True:
                    # Scan for assets
                    double_matches = scan_for_image("double.png")
                    charm_matches = scan_for_image("charm.png")
                    ethereal_matches = scan_for_image("ethereal.png")
                    
                    found_slot1 = False
                    found_slot2 = False
                    charm_found_slot1 = False
                    # Check Double matches
                    for m in double_matches:
                        if m['slot'] == 1: charm_found_slot1 = True

                    # Check Arcana matches
                    for m in charm_matches:
                        if m['slot'] == 1: found_slot1 = True
                        if m['slot'] == 2: found_slot2 = True
                        
                    # Check Spectral matches
                    for m in ethereal_matches:
                        if m['slot'] == 1: found_slot1 = True
                        if m['slot'] == 2: found_slot2 = True
                    
                    if (charm_found_slot1 or found_slot1)  and found_slot2:
                        logging.info("Skip tag on both slots")
                        arcana12()
                    elif found_slot1:
                        logging.info("Skip tag on slot 1")
                        arcana1()
                    elif found_slot2:
                        logging.info("Skip tag on slot 2")
                        arcana2()
                        
                    nouvelle_partie()
                    if keyboard.is_pressed("m"):
                        break
            elif keyboard.is_pressed("m"):
                pass
            elif keyboard.is_pressed("l"):
                break
        except Exception:
            pass

if __name__ == "__main__":
    balatro()
