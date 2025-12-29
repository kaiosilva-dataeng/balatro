import cv2
import numpy as np
import pyautogui
import pydirectinput
import keyboard
from PIL import Image
import time
import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ASSETS_DIR = BASE_DIR / "assets"
ASSETS_DIR.mkdir(exist_ok=True)
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR   / f"{time.strftime('%Y-%m-%d_%H-%M-%S')}.log"

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("Balatro Automation Ready.")

data = {
    "the_soul.png": {
        "confiance": 0.7,
        "needle": cv2.imread(str(ASSETS_DIR / "the_soul.png"))
    },
    "double.png": {
        "confiance": 0.9,
        "needle": cv2.imread(str(ASSETS_DIR / "double.png"))
    },
    "charm.png": {
        "confiance": 0.9,
        "needle": cv2.imread(str(ASSETS_DIR / "charm.png"))
    }
}


def scan_for_image(img_ref):
    """
    Scans the entire screen for the given image reference.
    Returns a list of found matches: [{'pos': (x, y), 'conf': float, 'slot': 1|2}]
    """
    if (needle := data[img_ref].get("needle")) is None:
        img_path = str(ASSETS_DIR / img_ref)
        needle = cv2.imread(img_path)

    if needle is None:
        logging.error(f"Could not load image: {img_ref}")
        return []

    try:

        pydirectinput.moveTo(5, 5)
        screenshot = pyautogui.screenshot()
        haystack = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        result = cv2.matchTemplate(haystack, needle, cv2.TM_CCOEFF_NORMED)
        
        threshold = data[img_ref].get("confiance", 0.6)
        
        loc = np.where(result >= threshold)
        matches = list(zip(*loc[::-1]))
        
        matches.sort(key=lambda pt: result[pt[1], pt[0]], reverse=True)
        
        found_objects = []
        processed_points = []
        
        for pt in matches:
            if any(abs(pt[0] - pp[0]) < 10 and abs(pt[1] - pp[1]) < 10 for pp in processed_points):
                continue
                
            processed_points.append(pt)
            confidence = result[pt[1], pt[0]]
            
            h, w = needle.shape[:2]
            center_x = pt[0] + w//2
            center_y = pt[1] + h//2
            
            slot = 1 if pt[0] < 750 else 2
            
            logging.info(f"Found {img_ref} | Slot {slot} | Conf: {confidence:.2f}")
            found_objects.append({'pos': (center_x, center_y), 'conf': float(confidence), 'slot': slot})
            
        return found_objects

    except Exception as e:
        logging.error(f"Error scanning for {img_ref}: {e}")
        return []


def buy_the_soul():
    time.sleep(5)
    soul_matches = scan_for_image("the_soul.png")
    
    if soul_matches:
        best = soul_matches[0]
        centre = best['pos']
        
        logging.info(f"Selecting SOUL card at {centre}")
        pydirectinput.moveTo(centre[0], centre[1])
        pydirectinput.click()
        time.sleep(1.5)

        pydirectinput.moveTo(centre[0], centre[1] + 100)
        pydirectinput.click()
        time.sleep(0.5)


def skip_slot_1():
    pydirectinput.moveTo(715, 850)
    pydirectinput.click()
    buy_the_soul()


def skip_slot_2():
    pydirectinput.moveTo(715, 850)
    pydirectinput.click()
    time.sleep(0.5)
    pydirectinput.moveTo(1070, 850)
    pydirectinput.click()
    buy_the_soul()


def skip_slot_1_buy_skip_slot_2():
    skip_slot_1()
    pydirectinput.moveTo(1335, 975)
    pydirectinput.click()
    time.sleep(0.5)
    pydirectinput.moveTo(1070, 850)
    pydirectinput.click()
    buy_the_soul()


def new_game():
    pydirectinput.press("esc")
    time.sleep(0.5)
    pydirectinput.moveTo(955, 355)
    pydirectinput.click()
    time.sleep(0.5)
    pydirectinput.moveTo(955, 830)
    pydirectinput.click()
    time.sleep(0.5)


def soul_farm() -> Path:
    print("Balatro Soul Farm Automation Ready.")
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
                    
                    found_slot1 = False
                    found_slot2 = False
                    charm_found_slot1 = False
                    # Check Double matches
                    for m in double_matches:
                        if m['slot'] == 1: charm_found_slot1 = True

                    # Check buy_the_soul matches
                    for m in charm_matches:
                        if m['slot'] == 1: found_slot1 = True
                        if m['slot'] == 2: found_slot2 = True
                        

                    if (charm_found_slot1 or found_slot1)  and found_slot2:
                        logging.info("Skip tag on both slots")
                        skip_slot_1_buy_skip_slot_2()
                    elif found_slot1:
                        logging.info("Skip tag on slot 1")
                        skip_slot_1()
                    elif found_slot2:
                        logging.info("Skip tag on slot 2")
                        skip_slot_2()
                        
                    new_game()
                    if keyboard.is_pressed("m"):
                        break
            elif keyboard.is_pressed("m"):
                pass
            elif keyboard.is_pressed("l"):
                break
        except Exception:
            pass
    return LOG_FILE

if __name__ == "__main__":
    print(f"Log file: {soul_farm()}")