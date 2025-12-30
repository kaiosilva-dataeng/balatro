import time

import keyboard
import pyautogui
from soul_farm import (
    CURRENT_HEIGHT,
    CURRENT_WIDTH,
    GAME_HEIGHT,
    GAME_WIDTH,
    OFFSET_X,
    OFFSET_Y,
    SCALE,
    scale_pos,
)


def diagnose():
    print("=== SCALING DIAGNOSTIC TOOL ===")
    print(f"Screen Res: {CURRENT_WIDTH}x{CURRENT_HEIGHT}")
    print(f"Game Rect:  {GAME_WIDTH}x{GAME_HEIGHT}")
    print(f"Scale:      {SCALE:.4f}")
    print(f"Offsets:    X={OFFSET_X}, Y={OFFSET_Y}")
    print("-------------------------------")

    targets = {
        "Skip Slot 1": (715, 850),
        "Skip Slot 2": (1070, 850),
        "New Game (Top)": (955, 355),
        "New Game (Bot)": (955, 830),
    }

    print("Calculated Targets:")
    for name, (tx, ty) in targets.items():
        sx, sy = scale_pos(tx, ty)
        print(f"  {name:15}: ({tx}, {ty}) -> ({sx}, {sy})")

    print("\n-------------------------------")
    print("INTERACTIVE CHECK:")
    print("1. Hover your mouse over 'Skip Slot 1' button.")
    print("2. Press 'C' to capture coordinates.")
    print("3. Press 'Q' to quit.")

    while True:
        if keyboard.is_pressed("c"):
            mx, my = pyautogui.position()
            print(f"\n[CAPTURE] Mouse at: ({mx}, {my})")

            # Reverse engineer to find what 1080p coord this maps to
            # mx = x * SCALE + OFFSET
            # x = (mx - OFFSET) / SCALE

            rx = (mx - OFFSET_X) / SCALE
            ry = (my - OFFSET_Y) / SCALE

            print(f"  Maps back to 1080p: ({int(rx)}, {int(ry)})")
            print("  Expected 'Skip Slot 1': (715, 850)")
            print(f"  Diff: Delta X={int(rx - 715)}, Delta Y={int(ry - 850)}")
            time.sleep(0.5)

        if keyboard.is_pressed("q"):
            break
        time.sleep(0.1)


if __name__ == "__main__":
    diagnose()
