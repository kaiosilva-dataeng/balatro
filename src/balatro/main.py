import random
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
        "nb_essais": 1000,
        "confiance": 0.5,
    },
    "arcana1.png": {
        "pos": [(570, 813)],
        "width": 64,
        "height": 64,
        "nb_essais": 3000,
        "confiance": 0.55,
    },
    "juggle.png": {
        "pos": [(570, 813)],
        "width": 64,
        "height": 64,
        "nb_essais": 3000,
        "confiance": 0.55,
    },
    "arcana2.png": {
        "pos": [(922, 873)],
        "width": 64,
        "height": 64,
        "nb_essais": 1000,
        "confiance": 0.8,
    },
    "foil.png": {
        "pos": [(922, 873)],
        "width": 64,
        "height": 64,
        "nb_essais": 1000,
        "confiance": 0.8,
    },
}


def reconnaissance_image(img_ref, ind=0):
    (x, y) = data[img_ref]["pos"][ind]
    width = data[img_ref]["width"]
    height = data[img_ref]["height"]
    nb_essais = data[img_ref]["nb_essais"]
    confiance = data[img_ref]["confiance"]

    # Capture screenshot in memory, no need to save to file
    im = pyautogui.screenshot(region=(x, y, width, height))
    pixels1 = list(im.getdata())

    # Open reference image from assets directory
    soul = Image.open(ASSETS_DIR / img_ref)
    pixels2 = list(soul.getdata())

    nb = 0
    for k in range(nb_essais):
        i = random.choice(pixels1)
        for j in pixels2:
            if (
                j[0] - 3 < i[0] < j[0] + 3
                and j[1] - 3 < i[1] < j[1] + 3
                and j[2] - 3 < i[2] < j[2] + 3
            ):
                nb += 1
                break

    return (nb / nb_essais) > confiance


def arcana():
    for i in range(5):
        if reconnaissance_image("soul.png", i):
            centre = (
                (2 * data["soul.png"]["pos"][i][0] + data["soul.png"]["width"]) // 2,
                (2 * data["soul.png"]["pos"][i][1] + data["soul.png"]["height"]) // 2,
            )
            pydirectinput.moveTo(centre[0], centre[1])
            pydirectinput.click()
            time.sleep(0.5)
            pydirectinput.moveTo(
                centre[0], centre[1] + (data["soul.png"]["height"] // 2) - 10
            )
            pydirectinput.click()
            time.sleep(5)
            break


def arcana1():
    pydirectinput.moveTo(715, 850)
    pydirectinput.click()
    time.sleep(5)
    arcana()


def arcana2():
    pydirectinput.moveTo(715, 850)
    pydirectinput.click()
    time.sleep(3)
    pydirectinput.moveTo(1070, 850)
    pydirectinput.click()
    time.sleep(5)
    arcana()


def arcana12():
    arcana1()
    pydirectinput.moveTo(1335, 975)
    pydirectinput.click()
    time.sleep(3)
    pydirectinput.moveTo(1070, 850)
    pydirectinput.click()
    time.sleep(5)
    arcana()


def nouvelle_partie():
    pydirectinput.press("esc")
    time.sleep(0.5)
    pydirectinput.moveTo(955, 355)
    pydirectinput.click()
    time.sleep(0.5)
    pydirectinput.moveTo(955, 830)
    pydirectinput.click()
    time.sleep(3)


def balatro():
    print("Balatro Automation Ready.")
    print("Press 'P' to start/resume.")
    print("Press 'M' to pause loop.")
    print("Press 'L' to exit completely.")
    while True:
        try:
            if keyboard.is_pressed("p"):
                while True:
                    if reconnaissance_image("arcana1.png") and not (
                        reconnaissance_image("juggle.png")
                    ):
                        if reconnaissance_image("arcana2.png") and not (
                            reconnaissance_image("foil.png")
                        ):
                            arcana12()
                        else:
                            arcana1()
                    elif reconnaissance_image("arcana2.png") and not (
                        reconnaissance_image("foil.png")
                    ):
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
