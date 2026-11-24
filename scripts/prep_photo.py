#!/usr/bin/env python3
"""
Prepare a portrait photo for ASCII conversion:
  1. cut out the subject (rembg)
  2. boost local contrast with CLAHE so facial features survive downsampling
  3. composite onto white and crop square around the subject

    python scripts/prep_photo.py <photo> [out.png]
Output (default): source-prepped.png, grayscale.
"""
import os
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
INP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "source-photo.jpg")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "source-prepped.png")

cut = remove(Image.open(INP).convert("RGBA"))
rgb = np.array(cut.convert("RGB"))
alpha = np.array(cut.split()[-1])
gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

clahe = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(8, 8))
gray = clahe.apply(gray)

# stretch tones over the subject only
lo, hi = np.percentile(gray[alpha > 128], [2, 97])
tone = np.clip((gray.astype(np.float32) - lo) / max(hi - lo, 1), 0, 1) * 255

mask = cv2.GaussianBlur(alpha.astype(np.float32) / 255.0, (0, 0), 1.0)
out = tone * mask + 255.0 * (1.0 - mask)

ys, xs = np.where(alpha > 20)
side = int(max(xs.max() - xs.min(), ys.max() - ys.min()) * 1.06)
cx, cy = (xs.min() + xs.max()) // 2, (ys.min() + ys.max()) // 2
canvas = np.full((side, side), 255, np.uint8)
x0, y0 = cx - side // 2, cy - side // 2
sx0, sy0 = max(x0, 0), max(y0, 0)
sx1, sy1 = min(x0 + side, out.shape[1]), min(y0 + side, out.shape[0])
canvas[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0] = out[sy0:sy1, sx0:sx1].astype(np.uint8)

Image.fromarray(canvas, mode="L").save(OUT)
print("wrote", OUT, canvas.shape)
