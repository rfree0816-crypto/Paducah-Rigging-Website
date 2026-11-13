from PIL import Image, ImageDraw, ImageOps
import numpy as np

def trim_bbox(im_rgb, thresh=700):
    arr = np.array(im_rgb)
    mask = arr.sum(axis=2) < thresh
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return im_rgb
    pad = 2
    x0 = max(xs.min()-pad, 0); x1 = min(xs.max()+pad, arr.shape[1])
    y0 = max(ys.min()-pad, 0); y1 = min(ys.max()+pad, arr.shape[0])
    return im_rgb.crop((x0, y0, x1, y1))

def make_white_chip(src_path, out_path, max_h=120, pad_ratio=0.12, radius=14):
    im = Image.open(src_path).convert('RGB')
    im = trim_bbox(im)
    w, h = im.size
    pad = int(max(w, h) * pad_ratio)
    canvas_w, canvas_h = w + pad*2, h + pad*2
    canvas = Image.new('RGB', (canvas_w, canvas_h), (255, 255, 255))
    canvas.paste(im, (pad, pad))
    # scale to max_h
    scale = max_h / canvas_h
    new_w, new_h = int(canvas_w * scale), max_h
    canvas = canvas.resize((new_w, new_h), Image.LANCZOS)
    # rounded mask
    rgba = canvas.convert('RGBA')
    mask = Image.new('L', (new_w, new_h), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([0,0,new_w-1,new_h-1], radius=radius, fill=255)
    rgba.putalpha(mask)
    rgba.save(out_path)
    print('saved', out_path, rgba.size)

make_white_chip('/home/user/webapp/.tmp/processed/tiger-logo-official.png', '/home/user/webapp/.tmp/processed/round2/brand-tiger.png')
make_white_chip('/home/user/webapp/.tmp/processed/cm-logo-official.png', '/home/user/webapp/.tmp/processed/round2/brand-cm.png', pad_ratio=0.18)
make_white_chip('/home/user/webapp/.tmp/processed/asr-logo-official.png', '/home/user/webapp/.tmp/processed/round2/brand-asr.png', pad_ratio=0.15)
