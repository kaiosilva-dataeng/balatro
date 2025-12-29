
import pyautogui
import pydirectinput
import keyboard
from PIL import Image
import time
from pathlib import Path

# Setup paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ASSETS_DIR = BASE_DIR / "assets"


data = {
    "soul.png": {
        "pos": [(620, 666), (795, 666), (970, 666), (1145, 666), (1320, 666)],
        "width": 148,
        "height": 220,

        "confiance": 0.8,
    },
    "arcana1.png": {
        "pos": [(570, 813)],
        "width": 64,
        "height": 64,

        "confiance": 0.9,
    },

    "arcana2.png": {
        "pos": [(922, 873)],
        "width": 64,
        "height": 64,

        "confiance": 0.8,
    },

    "spectral.png": {
        "pos": [(570, 813), (922, 873)],
        "width": 64,
        "height": 64,
        "confiance": 0.9,
    },
}


def reconnaissance_image(img_ref, ind=0):
    (x, y) = data[img_ref]["pos"][ind]
    width = data[img_ref]["width"]
    height = data[img_ref]["height"]
    confiance = data[img_ref]["confiance"]

    img_path = str(ASSETS_DIR / img_ref)
    
    try:
        location = pyautogui.locateOnScreen(
            img_path, 
            region=(x, y, width, height), 
            confidence=confiance
        )
        return location is not None
    except Exception:
        return False


def arcana():
    time.sleep(5)
    for i in range(5):
        if reconnaissance_image("soul.png", i):
            centre = (
                (2 * data["soul.png"]["pos"][i][0] + data["soul.png"]["width"]) // 2,
                (2 * data["soul.png"]["pos"][i][1] + data["soul.png"]["height"]) // 2,
            )
            pydirectinput.moveTo(centre[0], centre[1])
            pydirectinput.click()
            time.sleep(1.5)
            pydirectinput.moveTo(
                centre[0], centre[1] + (data["soul.png"]["height"] // 2) - 10
            )
            pydirectinput.click()
            time.sleep(0.5)
            break


def arcana1():
    pydirectinput.moveTo(715, 850)
    pydirectinput.click()
    arcana()


def arcana2():
    pydirectinput.moveTo(715, 850)
    pydirectinput.click()
    time.sleep(0.5)
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
                    has_arcana1 = reconnaissance_image("arcana1.png")
                    has_arcana2 = reconnaissance_image("arcana2.png")
                    has_spectral1 = reconnaissance_image("spectral.png", 0)
                    has_spectral2 = reconnaissance_image("spectral.png", 1)
                    
                    buy_slot1 = has_arcana1 or has_spectral1
                    buy_slot2 = has_arcana2 or has_spectral2
                    
                    if buy_slot1 and buy_slot2:
                        arcana12()
                    elif buy_slot1:
                        arcana1()
                    elif buy_slot2:
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


balatro()
