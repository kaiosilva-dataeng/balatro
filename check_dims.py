from PIL import Image
from pathlib import Path

ASSETS_DIR = Path("assets")
files = ['arcana1.png', 'arcana2.png', 'soul.png', 'spectral.png']

print("Checking dimensions...")
for f in files:
    try:
        p = ASSETS_DIR / f
        img = Image.open(p)
        print(f"{f}: {img.size}")
    except Exception as e:
        print(f"{f}: Error {e}")
