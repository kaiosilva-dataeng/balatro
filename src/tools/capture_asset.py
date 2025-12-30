import time
from pathlib import Path

import cv2
import keyboard
import numpy as np
import pyautogui

# Create assets dir if not exists
ASSETS_DIR = Path('assets')
ASSETS_DIR.mkdir(exist_ok=True)


def select_roi_and_save(filename):
    print(f'\n--- CAPTURING {filename} ---')
    print('1. Prepare the game screen so the card/asset is clearly visible.')
    print('2. When ready, switch to this window and press ENTER.')

    keyboard.wait('enter')
    print('Minimizing in 1 second...')
    time.sleep(1)

    # Capture full screen
    screenshot = pyautogui.screenshot()
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # Let user select ROI using OpenCV GUI
    print('Select the region of the asset with your mouse.')
    print('Press ENTER or SPACE after selecting to save.')
    print('Press C to cancel selection.')

    r = cv2.selectROI(
        f'Select {filename}', img, showCrosshair=True, fromCenter=False
    )
    cv2.destroyAllWindows()

    if r[2] == 0 or r[3] == 0:
        print('Selection cancelled or invalid.')
        return

    # Crop and save
    imCrop = img[int(r[1]) : int(r[1] + r[3]), int(r[0]) : int(r[0] + r[2])]
    save_path = ASSETS_DIR / filename
    cv2.imwrite(str(save_path), imCrop)
    print(f'✅ Saved {filename} to {save_path}')


if __name__ == '__main__':
    print('Asset Capture Tool')
    print('This will let you capture a new reference image.')

    target = input('Enter asset name: ').strip()
    if not target.endswith('.png'):
        target += '.png'

    select_roi_and_save(target)
