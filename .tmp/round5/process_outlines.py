from PIL import Image
import os

jobs = [
    ("crosby-outline-raw.png", "brand-crosby.png"),
    ("harrington-outline-raw.png", "brand-harrington.png"),
    ("tiger-outline-raw.png", "brand-tiger.png"),
    ("blackbear-outline-raw.png", "brand-blackbear.png"),
    ("cm-outline-raw.png", "brand-cm.png"),
    ("asr-outline-raw.png", "brand-asr.png"),
]

src_dir = "/home/user/webapp/.tmp/round5"
dst_dir = "/home/user/webapp/images"
TARGET_H = 200  # retina-ish height, CSS displays at 34px

for src_name, dst_name in jobs:
    src = os.path.join(src_dir, src_name)
    dst = os.path.join(dst_dir, dst_name)
    img = Image.open(src).convert("RGBA")

    # Trim to bounding box of non-transparent content
    alpha = img.split()[-1]
    bbox = alpha.getbbox()
    if bbox:
        # add a small margin
        margin = int(0.04 * max(img.size))
        l, t, r, b = bbox
        l = max(0, l - margin)
        t = max(0, t - margin)
        r = min(img.width, r + margin)
        b = min(img.height, b + margin)
        img = img.crop((l, t, r, b))

    # Resize keeping aspect ratio, height = TARGET_H
    w, h = img.size
    new_w = int(w * (TARGET_H / h))
    img = img.resize((new_w, TARGET_H), Image.LANCZOS)

    img.save(dst, "PNG")
    print(dst_name, img.size)
