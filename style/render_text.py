"""Render a Hookforge/CapCut text card exactly like the team's CapCut default (see capcut_text_preset.json).
Usage: render_card(text, W, H, scale=..., y=...) -> RGBA PIL image same size as the frame; or burn onto a frame.
Calibrated against posted reels (STYLE_GUIDE.md §Verification). Font: CapCut SystemFont en.ttf ≈ Montserrat Medium (OFL).
"""
import json, os, re
from PIL import Image, ImageDraw, ImageFont
import emoji as _emoji
HERE = os.path.dirname(os.path.abspath(__file__))
PRESET = json.load(open(os.path.join(HERE, "capcut_text_preset.json")))
EMOJI_FONT = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"

def _font(px):
    ff = PRESET["render"]["font_file_box"]
    if not os.path.exists(ff): ff = os.path.join(HERE, "..", "assets", "fonts", "Montserrat-VariableFont_wght.ttf")   # vendored (OFL)
    f = ImageFont.truetype(ff, int(round(px)))
    try: f.set_variation_by_name(PRESET["render"]["font_variation"].encode())
    except Exception: pass
    return f

def _runs(line):
    out, i = [], 0
    for e in _emoji.emoji_list(line):
        if e["match_start"] > i: out.append(("t", line[i:e["match_start"]]))
        out.append(("e", e["emoji"])); i = e["match_end"]
    if i < len(line): out.append(("t", line[i:]))
    return out

def _emoji_img(e, px):
    f = ImageFont.truetype(EMOJI_FONT, 109)
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((10, 10), e, font=f, embedded_color=True)
    bb = im.getbbox() or (0, 0, 1, 1); im = im.crop(bb)
    h = int(round(px * PRESET["render"]["emoji_height_em"])); w = max(1, int(round(im.width * h / max(1, im.height))))
    return im.resize((w, h), Image.LANCZOS)

def _line_width(runs, f, px, sw):
    w = 0
    for k, s in runs:
        if k == "t": w += f.getlength(s)
        else: w += px * PRESET["render"]["emoji_height_em"] * 1.0 + px * 0.05
    return w

def wrap(text, f, px, sw, max_w):
    lines = []
    for para in text.split("\n"):
        words = para.split(" "); cur = ""
        for wd in words:
            t = (cur + " " + wd) if cur else wd
            if _line_width(_runs(t), f, px, sw) <= max_w or not cur: cur = t
            else: lines.append(cur); cur = wd
        lines.append(cur)
    return [l.rstrip() for l in lines]

def render_card(text, W, H, scale=None, y=None, x=0.0, size=None, stroke_width=None, fill=None, stroke_color=None):
    P = PRESET; R = P["render"]
    scale = P["default"]["scale"] if scale is None else scale
    y = P["default"]["transform_y"] if y is None else y
    size = P["default"]["font_size"] if size is None else size
    sw_rel = P["default"]["stroke_width"] if stroke_width is None else stroke_width
    px = R["px_per_size_unit_per_canvas_width"] * size * scale * W
    sw = max(0, int(round(px * sw_rel * R["stroke_px_per_capcut_width_em"])))
    f = _font(px)
    lines = wrap(text, f, px, sw, P["default"]["line_max_width"] * W * scale if R.get("wrap_scales") else P["default"]["line_max_width"] * W)
    asc, desc = f.getmetrics(); lh = (asc + desc) * (1 + P["default"]["line_spacing"]) * R["line_height_factor"]
    block_h = lh * len(lines)
    cx = (1 + x) / 2 * W; cy = (1 - y) / 2 * H
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    top = cy - block_h / 2
    for i, line in enumerate(lines):
        runs = _runs(line); lw = _line_width(runs, f, px, sw); xx = cx - lw / 2; yy = top + i * lh
        for k, s in runs:
            if k == "t":
                d.text((xx, yy), s, font=f, fill=fill or P["default"]["fill"], stroke_width=sw, stroke_fill=stroke_color or P["default"]["stroke_color"])
                xx += f.getlength(s)
            else:
                ei = _emoji_img(s, px); ey = int(yy + asc - px * R["emoji_baseline_drop_em"] - ei.height)
                layer.alpha_composite(ei, (int(xx + px * 0.025), max(0, ey))); xx += ei.width + px * 0.05
    return layer

def burn(frame_path, out_path, text, **kw):
    im = Image.open(frame_path).convert("RGBA"); W, H = im.size
    im.alpha_composite(render_card(text, W, H, **kw)); im.convert("RGB").save(out_path)
