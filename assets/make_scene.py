# Profile banner: a night studio built from the CC0 "Lofi Breeze" pixel-art pack (OpenGameArt),
# customised for Emmanuel: EMEMZY neon sign, NaijaVox / Bùkà Hustle / LAST BUS posters, an Axiveri cube,
# string lights, a voice waveform on the wall screen. Animated: typing, coffee maker, neon flicker, lights.
# Usage: python make_scene.py <pack_dir> <font.ttf>  ->  assets/banner.gif
import sys, os, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

PACK, FONT = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
W, H, S = 320, 180, 4
SP = os.path.join(PACK, "single-pngs"); GF = os.path.join(PACK, "gifs")

def png(n): return Image.open(os.path.join(SP, n)).convert("RGBA")
def gif_frames(n):
    im = Image.open(os.path.join(GF, n)); fr = []
    for i in range(im.n_frames):
        im.seek(i); fr.append(im.convert("RGBA").copy())
    return fr
obj1, obj3 = png("scene_objects1.png"), png("scene_objects3.png")
couch = obj1.crop((31, 108, 117, 150)); shelf = obj1.crop((382, 84, 424, 150)); rack = obj1.crop((229, 66, 294, 150))
win_wide = obj3.crop((301, 60, 379, 106))
floor_strip = obj3.crop((0, 140, 450, 153))
SKIN = {(215, 171, 132): (122, 76, 46), (192, 126, 100): (92, 55, 32)}
def reskin(f):
    px = f.load()
    for y in range(f.height):
        for x in range(f.width):
            p = px[x, y]
            if p[3] and p[:3] in SKIN: px[x, y] = SKIN[p[:3]] + (255,)
    return f
typing = [reskin(f.crop((23, 96, 106, 150))) for f in gif_frames("guy_typing.gif")]
coffee = [f.crop((16, 21, 35, 39)) for f in gif_frames("coffeemaker.gif")]
wall = png("scene_bluewall.png")

def font(sz): return ImageFont.truetype(FONT, sz)

def base():
    im = Image.new("RGBA", (W, H), (20, 24, 48, 255))
    for x in range(0, W, wall.width): im.alpha_composite(wall, (x, 0))
    # darker band for depth + floor
    for x in range(0, W, floor_strip.width): im.alpha_composite(floor_strip, (x, 150))
    d = ImageDraw.Draw(im); d.rectangle((0, 163, W, H), fill=(40, 20, 22, 255))
    for y in range(163, H, 4): d.line((0, y, W, y), fill=(52, 26, 28, 255))
    # floorboards below the brick line
    for k, y in enumerate(range(163, H, 5)):
        d.rectangle((0, y, W, y + 4), fill=(46, 28, 24, 255) if k % 2 else (54, 33, 27, 255)); d.line((0, y, W, y), fill=(64, 40, 32, 255))
        for x in range((k * 23) % 37, W, 37): d.line((x, y, x, y + 4), fill=(34, 20, 17, 255))
    return im

def poster(im, x, y, w, h, bg, draw_fn):
    d = ImageDraw.Draw(im)
    d.rectangle((x - 1, y - 1, x + w, y + h), fill=(230, 232, 245, 255)); d.rectangle((x, y, x + w - 1, y + h - 1), fill=bg)
    d.line((x - 1, y + h + 1, x + w, y + h + 1), fill=(0, 0, 0, 90))
    draw_fn(d)

def scene(i):
    im = base(); d = ImageDraw.Draw(im)
    # string lights
    cols = [(255, 95, 126), (255, 209, 102), (126, 224, 255), (167, 139, 250), (126, 231, 135)]
    for x in range(0, W, 2):
        y = 5 + int(3 * math.sin(x / 20) ** 2)
        d.point((x, y), fill=(40, 46, 80, 255))
        if x % 14 == 6:
            c = cols[(x // 14 + i // 3) % 5]
            d.rectangle((x, y + 1, x + 1, y + 2), fill=c if (x // 14 + i) % 4 else tuple(v // 2 for v in c))
    # window (night city) above the couch
    im.alpha_composite(win_wide, (12, 44))
    # neon sign with glow (flickers on two frames)
    dim = i in (9, 10)
    glow = Image.new("RGBA", (W, H)); gd = ImageDraw.Draw(glow)
    gd.text((206, 40), "EMEMZY", font=font(16), fill=(255, 79, 216, 255)); gd.text((216, 58), "VISUALS", font=font(8), fill=(126, 224, 255, 255))
    blur = glow.filter(ImageFilter.GaussianBlur(3))
    a = 0.55 if dim else 1.0
    for layer in (blur, blur, glow):
        L = layer.copy(); L.putalpha(L.split()[3].point(lambda v: int(v * a))); im.alpha_composite(L)
    # posters drawn on their own layer, then placed (shifted into the close-up framing)
    _im, _d = im, d
    im = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(im)
    # posters: NaijaVox (voice wave), Bùkà Hustle (pot), LAST BUS (danfo)
    def naijavox(d):
        for k in range(14):
            h = [2, 4, 7, 10, 5, 12, 8, 4, 9, 13, 7, 4, 10, 5][k]
            h = max(1, int(h * (0.6 + 0.4 * abs(math.sin((i + k) * 0.7)))))
            d.line((100 + k * 2, 66 - h // 2, 100 + k * 2, 66 + h // 2), fill=[(126, 224, 255), (167, 139, 250), (244, 114, 182)][k % 3])
    poster(im, 97, 54, 32, 24, (16, 22, 48, 255), naijavox)
    d.text((99, 73), "NAIJAVOX", font=font(4) if False else font(8), fill=(154, 163, 214, 255)) if False else None
    def buka(d):
        d.rectangle((141, 62, 151, 69), fill=(60, 60, 60)); d.rectangle((141, 61, 151, 62), fill=(228, 87, 46)); d.line((139, 70, 153, 70), fill=(90, 90, 90))
        for k in range(3): d.point((143 + k * 3, 58 - (i + k) % 3), fill=(200, 200, 200))
    poster(im, 136, 54, 22, 20, (43, 26, 14, 255), buka)
    def bus(d):
        d.rectangle((168, 62, 186, 68), fill=(232, 185, 35)); [d.rectangle((169 + k * 4, 63, 171 + k * 4, 64), fill=(42, 60, 90)) for k in range(4)]
        d.point((168, 65), fill=(255, 242, 168) if i % 4 < 2 else (120, 110, 60)); d.rectangle((170, 68, 172, 69), fill=(20, 20, 20)); d.rectangle((182, 68, 184, 69), fill=(20, 20, 20))
    poster(im, 165, 56, 24, 16, (18, 12, 30, 255), bus)
    layer = im; im, d = _im, _d
    im.alpha_composite(layer, (22, 12))
    # furniture
    im.alpha_composite(couch, (6, 150 - couch.height))
    im.alpha_composite(shelf, (96, 150 - shelf.height))
    im.alpha_composite(rack, (246, 150 - rack.height))
    # coffee maker + Axiveri cube on top of the bookshelf
    # (coffee maker left out of the close-up framing)
    # the developer typing at his desk (centre)
    t = typing[i % len(typing)]
    im.alpha_composite(t, (152, 150 - t.height))
    # small plant by the rack
    d.rectangle((236, 143, 242, 149), fill=(194, 109, 60)); [d.line((237 + k * 2, 143, 237 + k * 2, 136 + (k % 2) * 2), fill=(63, 163, 77)) for k in range(3)]
    # soft monitor glow + vignette
    gl = Image.new("RGBA", (W, H)); ImageDraw.Draw(gl).ellipse((150, 80, 240, 150), fill=(90, 180, 255, 40)); im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(14)))
    return im

def hud(big, i):
    # crisp pixel-font text drawn at full size (Press Start 2P works best at multiples of 8)
    d = ImageDraw.Draw(big)
    def t(x, y, s, sz, col):
        f = ImageFont.truetype(FONT, sz)
        d.text((x, y), s, font=f, fill=col)
    d = ImageDraw.Draw(big)
    t(48, 48, "HI, I'M EMMANUEL", 32, (255, 255, 255))
    t(50, 100, "ML ENGINEER @ PLOTWEAVER", 16, (180, 205, 255))
    t(50, 130, "FOUNDER @ AXIVERI", 16, (255, 150, 70))
    t(48, 664, "$ teaching machines to speak African languages" + ("_" if i % 8 < 4 else ""), 16, (126, 231, 135))
    return big
CROP = (92, 34, 306, 154)  # close-up on the desk, 214 x 120 art pixels, shown 6x
def closeup(im):
    c = im.crop(CROP).resize(((CROP[2] - CROP[0]) * 6, (CROP[3] - CROP[1]) * 6), Image.NEAREST)
    return c.crop((0, 0, 1280, 720))
frames = [hud(closeup(scene(i).convert("RGB")), i) for i in range(24)]
pal = [f.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE) for f in frames]
out = os.path.join(HERE, "banner.gif")
pal[0].save(out, save_all=True, append_images=pal[1:], duration=120, loop=0, optimize=True, disposal=1)
frames[0].save(os.path.join(HERE, "banner_frame.png"))
print("ok", os.path.getsize(out) // 1024, "KB")
