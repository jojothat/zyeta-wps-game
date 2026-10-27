"""Soften the Office 2.0 game palette: lower chroma in OKLab, slight lift, every colour and every baked image.
usage: python3 soften.py in.html out.html --chroma 0.72 --lift 0.04 --warm 0.0"""
import re, sys, base64, io, argparse
import numpy as np
from PIL import Image

def srgb_to_lin(c): return np.where(c <= 0.04045, c/12.92, ((c+0.055)/1.055)**2.4)
def lin_to_srgb(c): c=np.clip(c,0,1); return np.where(c <= 0.0031308, c*12.92, 1.055*c**(1/2.4)-0.055)
M1=np.array([[0.4122214708,0.5363325363,0.0514459929],[0.2119034982,0.6806995451,0.1073969566],[0.0883024619,0.2817188376,0.6299787005]])
M2=np.array([[0.2104542553,0.7936177850,-0.0040720468],[1.9779984951,-2.4285922050,0.4505937099],[0.0259040371,0.7827717662,-0.8086757660]])
M1i=np.linalg.inv(M1); M2i=np.linalg.inv(M2)
def to_lab(rgb): return np.cbrt(srgb_to_lin(rgb) @ M1.T) @ M2.T
def from_lab(lab): return lin_to_srgb(((lab @ M2i.T)**3) @ M1i.T)

PAPER = to_lab(np.array([[0xF6,0xF4,0xEF]])/255.0)[0]
def soften(rgb, a):
    lab = to_lab(rgb)
    C = np.hypot(lab[...,1], lab[...,2])
    # stronger reduction on the most saturated colours, near-greys untouched
    k = a.chroma + (1-a.chroma) * np.exp(-(C/0.06)**2)
    lab[...,1] *= k; lab[...,2] *= k
    L = lab[...,0]
    lab[...,0] = L + a.lift * (1-L) * np.clip((L-0.15)/0.5, 0, 1)   # lift mids/darks a little, keep near-black ink
    if a.warm: lab = lab*(1-a.warm) + PAPER*a.warm
    return np.clip(from_lab(lab), 0, 1)

def hexfix(m, a):
    h = m.group(0); rgb = np.array([[int(h[i:i+2],16) for i in (1,3,5)]])/255.0
    out = (soften(rgb, a)[0]*255+0.5).astype(int)
    return '#%02X%02X%02X' % tuple(out)

def imgfix(m, a, q):
    im = Image.open(io.BytesIO(base64.b64decode(m.group(1)))).convert('RGBA')
    arr = np.asarray(im).astype(np.float64)/255.0
    rgb = soften(arr[...,:3], a)
    out = np.dstack([rgb, arr[...,3:]]); out = (out*255+0.5).astype(np.uint8)
    buf = io.BytesIO(); Image.fromarray(out, 'RGBA').save(buf, 'WEBP', quality=q, method=6, alpha_quality=100)
    return 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode()


from types import SimpleNamespace as NS
from multiprocessing import Pool
def _job(args):
    b64, a, q = args
    class M:
        def group(self, n): return b64
    return imgfix(M(), a, q)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('src'); ap.add_argument('dst')
    ap.add_argument('--env', default='0.65,0.05,0.0', help='chroma,lift,warm for the scene floors/backdrops')
    ap.add_argument('--spr', default='0.80,0.03,0.0', help='chroma,lift,warm for sprites, avatars, tiles')
    ap.add_argument('--ui', default='0.78,0.0,0.0', help='chroma,lift,warm for CSS/scene hex colours')
    ap.add_argument('--q', type=int, default=90)
    a = ap.parse_args()
    mk = lambda t: NS(**dict(zip(('chroma','lift','warm'), map(float, t.split(',')))))
    E, S, U = mk(a.env), mk(a.spr), mk(a.ui)
    h = open(a.src, encoding='utf-8').read()
    e0 = h.index('window.O2_ENVS'); e1 = h.index('</script>', e0)
    rx = re.compile(r'data:image/webp;base64,([A-Za-z0-9+/=]+)')
    ms = list(rx.finditer(h))
    jobs = [(m.group(1), E if e0 <= m.start() < e1 else S, a.q) for m in ms]
    with Pool() as pool: outs = pool.map(_job, jobs)
    parts, last = [], 0
    for m, o in zip(ms, outs): parts += [h[last:m.start()], o]; last = m.end()
    parts.append(h[last:]); h = ''.join(parts)
    h = re.sub(r'#[0-9A-Fa-f]{6}\b', lambda m: hexfix(m, U), h)
    open(a.dst, 'w', encoding='utf-8').write(h)
    print('wrote', a.dst, len(h), 'images', len(ms), 'env', sum(1 for j in jobs if j[1] is E))
