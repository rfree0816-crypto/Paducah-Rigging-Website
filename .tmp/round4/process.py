import sys
from PIL import Image
import numpy as np

def whiten_bg(im):
    im = im.convert('RGB')
    arr = np.array(im).astype(np.int16)
    r,g,b = arr[...,0], arr[...,1], arr[...,2]
    mx = np.max(arr, axis=-1)
    mn = np.min(arr, axis=-1)
    gray = (mx.astype(np.int32)+mn.astype(np.int32))//2
    sat = np.where(mx>0, (mx-mn)*255//np.maximum(mx,1), 0)
    mask = (gray > 225) & (sat < 12)
    arr[mask] = [255,255,255]
    return Image.fromarray(arr.astype(np.uint8), 'RGB')

def process(src, dst, size=(1024,684), whiten=True):
    im = Image.open(src)
    if whiten:
        im = whiten_bg(im)
    im = im.resize(size, Image.LANCZOS)
    im.save(dst, 'JPEG', quality=90)
    print(dst, im.size)

if __name__ == '__main__':
    base = '/home/user/webapp/.tmp/round4/'
    out = '/home/user/webapp/images/'
    jobs = [
        ('shackles-ai-raw.jpg', 'shackles.jpg', True),
        ('hooks-ai-raw.jpg', 'hooks.jpg', True),
        ('wireropeclips-ai-raw.jpg', 'wire-rope-clips.jpg', True),
        ('masterlinks-ai-raw.jpg', 'master-links.jpg', True),
        ('binders-ai-raw.jpg', 'binders.jpg', True),
        ('rope-ai-raw.jpg', 'rope.jpg', True),
        ('rope-blue-ai-raw.jpg', 'rope-ultra-blue.jpg', True),
        ('nylonslings-ai-raw.jpg', 'nylon-slings.jpg', False),
    ]
    for src, dst, whiten in jobs:
        process(base+src, out+dst, whiten=whiten)
