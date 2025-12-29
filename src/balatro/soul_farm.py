"""
Module for the Balatro Soul Farm automation.
"""
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

import cv2
import keyboard
import numpy as np
import pyautogui
import pydirectinput
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
ASSETS_DIR.mkdir(exist_ok=True)
LOG_DIR = Path.home() / ".balatro" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR   / f"{time.strftime('%Y-%m-%d_%H-%M-%S')}.log"

import sys

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logging.info("Balatro Automation Ready.")
logging.info(f"Resolution: {pyautogui.size()}")
# --- Configuration Loading ---
import json
CONFIG_FILE = BASE_DIR / "config.json"

CONFIG = {
    "window": (1920, 1080),
    "skip_slot_1": (715, 850),
    "skip_slot_2": (1070, 850),
    "package_specialized_skip": (1335, 975),
    "new_game_top": (955, 355),
    "new_game_confirm": (955, 830)
}

def load_config():
    """Loads configuration from file if it exists."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                user_config = json.load(f)
                CONFIG.update(user_config)
                logging.info(f"Loaded configuration from {CONFIG_FILE}")
        except Exception as e:
            logging.error(f"Failed to load config.json: {e}")
    else:
        logging.warning(f"Config file not found at {CONFIG_FILE}. Using default 1080p coordinates.")

load_config()

def get_action_pos(action_name: str) -> tuple[int, int]:
    """Retrieves the (x, y) coordinates for a named action from the config."""
    return tuple(CONFIG.get(action_name, (0, 0)))

# -------------------------

data = {
    "the_soul.png": {
        "confiance": 0.7,
        "needle": cv2.imread(str(ASSETS_DIR / "the_soul.png"))
    },
    "double.png": {
        "confiance": 0.90,
        "needle": cv2.imread(str(ASSETS_DIR / "double.png"))
    },
    "charm.png": {
        "confiance": 0.90,
        "needle": cv2.imread(str(ASSETS_DIR / "charm.png"))
    }
}


def scan_screen(asset_names: List[str]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Scans the screen once for multiple assets.
    
    Args:
        asset_names (List[str]): List of image filenames to search for.
        
    Returns:
        Dict[str, List[Dict]]: Dictionary mapping asset name to list of found matches.
    """
    results = {name: [] for name in asset_names}
    
    try:
        time.sleep(0.1)
        screenshot = pyautogui.screenshot()
        haystack = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        # Calculate split point dynamically from config once per scan
        s1 = get_action_pos("skip_slot_1")
        s2 = get_action_pos("skip_slot_2")
        if s1 and s2 and s1[0] > 0 and s2[0] > 0:
            split_x = (s1[0] + s2[0]) // 2
        else:
            split_x = 750

        for img_ref in asset_names:
            if (needle := data[img_ref].get("needle")) is None:
                img_path = str(ASSETS_DIR / img_ref)
                needle = cv2.imread(img_path)
            
            if needle is None:
                logging.error(f"Could not load image: {img_ref}")
                continue

            res = cv2.matchTemplate(haystack, needle, cv2.TM_CCOEFF_NORMED)
            threshold = data[img_ref].get("confiance", 0.6)
            loc = np.where(res >= threshold)
            matches = list(zip(*loc[::-1]))
            matches.sort(key=lambda pt: res[pt[1], pt[0]], reverse=True)
            
            processed_points = []
            
            for pt in matches:
                if any(abs(pt[0] - pp[0]) < 10 and abs(pt[1] - pp[1]) < 10 for pp in processed_points):
                    continue
                    
                processed_points.append(pt)
                confidence = res[pt[1], pt[0]]
                
                h, w = needle.shape[:2]
                center_x = pt[0] + w//2
                center_y = pt[1] + h//2
                
                slot = 1 if pt[0] < split_x else 2
                
                logging.info(f"Found {img_ref} | Slot {slot} | Conf: {confidence:.2f}")
                results[img_ref].append({'pos': (center_x, center_y), 'conf': float(confidence), 'slot': slot})
                
    except Exception as e:
        logging.error(f"Error in scan_screen: {e}")
        
    return results

def scan_for_image(img_ref: str) -> List[Dict[str, Any]]:
    """Legacy wrapper for single image scan."""
    return scan_screen([img_ref]).get(img_ref, [])


def buy_the_soul() -> None:
    """
    Attempts to find and click the 'The Soul' card on the screen.
    """
    time.sleep(5)
    # Still uses single scan as it is a specific action step
    soul_matches = scan_for_image("the_soul.png")
    
    if soul_matches:
        best = soul_matches[0]
        centre = best['pos']
        
        logging.info(f"Selecting SOUL card at {centre}")
        pydirectinput.moveTo(centre[0], centre[1])
        pydirectinput.click()
        time.sleep(1.5)

        # Click "Use" button (assumed +100 px down). 
        # Ideally this should be calibrated too, or we search for "Use" button image.
        # For now, literal +100.
        pydirectinput.moveTo(centre[0], centre[1] + 100)
        pydirectinput.click()
        time.sleep(0.5)


# --- Atomic UI Actions ---
def click_skip_slot_1_button():
    """Clicks the button to skip the first slot (Small Blind)."""
    pydirectinput.moveTo(*get_action_pos("skip_slot_1"))
    pydirectinput.click()
    logging.info("ACTION: Skipped Slot 1")

def click_skip_slot_2_button():
    """Clicks the button to skip the second slot (Big Blind)."""
    pydirectinput.moveTo(*get_action_pos("skip_slot_2"))
    pydirectinput.click()
    logging.info("ACTION: Skipped Slot 2")

def click_buy_specialized_skip_button():
    """Clicks the specialized skip/next button."""
    pydirectinput.moveTo(*get_action_pos("package_specialized_skip"))
    pydirectinput.click()
    logging.info("ACTION: Bought Specialized Skip/Next")

def click_new_game_top():
    """Clicks the top New Game button in menu."""
    pydirectinput.moveTo(*get_action_pos("new_game_top"))
    pydirectinput.click()

def click_new_game_confirm():
    """Clicks the confirm New Game button."""
    pydirectinput.moveTo(*get_action_pos("new_game_confirm"))
    pydirectinput.click()
# -------------------------

def skip_slot_1() -> None:
    """
    Skips the first tag slot and then checks for the soul card.
    """
    click_skip_slot_1_button()
    buy_the_soul()


def skip_slot_2() -> None:
    """
    Skips the second tag slot and then checks for the soul card.
    Note: Current logic implies clicking slot 1 skip button is required/part of flow.
    """
    click_skip_slot_1_button() # "same as skip_slot_1..."
    time.sleep(0.5)
    click_skip_slot_2_button() # "really second skip slot"
    buy_the_soul()


def skip_slot_1_buy_skip_slot_2() -> None:
    """
    Skips the first tag slot, buys a specialized pack/skip, skips the second slot, and checks for the soul card.
    """
    click_skip_slot_1_button()
    buy_the_soul() # "coupled pick card handler" checks for soul after first skip
    
    click_buy_specialized_skip_button()
    time.sleep(0.5)
    
    click_skip_slot_2_button()
    buy_the_soul()


def new_game() -> None:
    """
    Resets the game state by returning to the main menu and starting a new run.
    """
    pydirectinput.press("esc")
    time.sleep(0.5)
    click_new_game_top()
    time.sleep(0.5)
    click_new_game_confirm()
    time.sleep(0.5)
    pydirectinput.moveTo(5, 5)
    time.sleep(3)
    logging.info("ACTION: New Game Started")

def soul_farm() -> Path:
    """
    Main loop for the Soul Farm automation.
    Uses keyboard hooks to toggle states asynchronously.
    
    Returns:
        Path: The path to the log file generated for this session.
    """
    print("Balatro Soul Farm Automation Ready.")
    print(f"Loaded Configuration: {CONFIG}")
    print("Press 'P' to start/resume.")
    print("Press 'M' to pause loop.")
    print("Press 'L' to exit completely.")

    # State container to be modified by callbacks
    class State:
        running: bool = True
        farming: bool = False
    
    state = State()

    def on_p(event):
        if not state.farming:
            print("\n[Resuming Automation]")
            state.farming = True

    def on_m(event):
        if state.farming:
            print("\n[Pausing Automation]")
            state.farming = False

    def on_l(event):
        print("\n[Stopping Automation]")
        state.running = False
        state.farming = False

    # Hook keys
    keyboard.unhook_all()
    keyboard.on_press_key("p", on_p)
    keyboard.on_press_key("m", on_m)
    keyboard.on_press_key("l", on_l)

    while state.running:
        try:
            if state.farming:
                # Optimized Single-Pass Scan
                scan_results = scan_screen(["double.png", "charm.png"])
                double_matches = scan_results["double.png"]
                charm_matches = scan_results["charm.png"]
                
                found_slot1 = False
                found_slot2 = False
                double_found_slot1 = False
                
                # Check Double matches
                for m in double_matches:
                    if m['slot'] == 1: double_found_slot1 = True

                # Check charm matches (logic seems to treat charm same as soul trigger?)
                for m in charm_matches:
                    if m['slot'] == 1: found_slot1 = True
                    if m['slot'] == 2: found_slot2 = True
                
                # Succinct Scan Log
                detection_summary = []
                if double_found_slot1: detection_summary.append("Double(Slot1)")
                if found_slot1: detection_summary.append("Charm(Slot1)")
                if found_slot2: detection_summary.append("Charm(Slot2)")
                
                if detection_summary:
                    logging.info(f"SCAN_RESULT: detected {', '.join(detection_summary)}")
                
                if double_found_slot1 and found_slot2:
                    logging.info("DECISION: Skip for double and charm")
                    skip_slot_1_buy_skip_slot_2()
                elif found_slot1 and found_slot2:
                    logging.info("DECISION: Skip for charm and charm")
                    skip_slot_1_buy_skip_slot_2()
                elif found_slot1:
                    logging.info("DECISION: Skip for charm (slot 1)")
                    skip_slot_1()
                elif found_slot2:
                    logging.info("DECISION: Skip for charm (slot 2)")
                    skip_slot_2()
                    
                new_game()
            else:
                # Idle wait to reduce CPU usage when paused
                time.sleep(0.1)
                
        except Exception as e:
            logging.error(f"Error in main loop: {e}")
            time.sleep(1)

    keyboard.unhook_all()
    return LOG_FILE

if __name__ == "__main__":
    print(f"Log file: {soul_farm()}")