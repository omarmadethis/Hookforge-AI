"""Hookforge text cards with Apple iOS emoji (D61, Omar 2026-10-19: "emojis must be Apple iOS emojis").

Wraps style/render_text.py (owned by the style worker; NOT edited) and swaps two internals at call time:
  * emoji -> Apple Color Emoji PNG (160 px art from iamcal/emoji-data img-apple-160, cached in assets/emoji_apple/160/;
    fallback: the 96 px CBDT strike of assets/emoji_apple/AppleColorEmoji-Linux.ttf). Never Noto.
  * font  -> Montserrat at weight 560 with stroke 0.091*font_px. Calibrated 2026-10-19 on Omar's own MerryGlow reel
    (refs/omar_ref_mg.mp4, "The problem... 🤕", 2160x3848): stem 18 px, outline 16 px, cap-to-descender 162 px,
    block centre 21.2 % from top (CapCut transform_y 0.576). CapCut "first preset style + stroke thickness 45"
    = fill #FFFFFF, stroke #000000 width 0.09 in draft JSON (UI 0-100 maps to width 0-0.2).
House card rule (D61): one 'then' card per problem scene, then "Vs... ⏰", then the solution card over all afters.
"""
import os, sys, io, json, urllib.request
from PIL import Image, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "style"))
import render_text as RT
EDIR = os.path.join(REPO, "assets", "emoji_apple"); E160 = os.path.join(EDIR, "160"); ETTF = os.path.join(EDIR, "AppleColorEmoji-Linux.ttf")
SRC160 = "https://raw.githubusercontent.com/iamcal/emoji-data/master/img-apple-160/{}"
MONT = "/usr/share/fonts/truetype/sand-box/google/Montserrat/Montserrat-VariableFont_wght.ttf"
CAL = dict(weight=560, font_px_per_W=0.081, stroke_per_px=0.091, transform_y=0.576, emoji_h_em=1.0)
_IDX = None

def _index():
    global _IDX
    if _IDX is None:
        _IDX = {}
        for e in json.load(open(os.path.join(EDIR, "emoji.json"))):
            for k in [e["unified"]] + (e.get("non_qualified") and [e["non_qualified"]] or []):
                _IDX[k.upper()] = e["image"]
    return _IDX

def _key(ch): return "-".join("%04X" % ord(c) for c in ch)

def apple_png(ch):
    """Path to a 160 px Apple emoji PNG (transparent). Downloads once into assets/emoji_apple/160/."""
    idx = _index(); k = _key(ch); name = idx.get(k) or idx.get(k.replace("-FE0F", "")) or (k.lower() + ".png")
    p = os.path.join(E160, name)
    if not os.path.exists(p):
        os.makedirs(E160, exist_ok=True)
        try:
            data = urllib.request.urlopen(SRC160.format(name), timeout=20).read(); Image.open(io.BytesIO(data)).verify()
            open(p, "wb").write(data)
        except Exception:
            f = ImageFont.truetype(ETTF, 96); im = Image.new("RGBA", (130, 130), (0, 0, 0, 0))
            from PIL import ImageDraw; ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True)
            im.crop(im.getbbox()).save(p)
    return p

def _emoji_img(e, px):
    im = Image.open(apple_png(e)).convert("RGBA"); im = im.crop(im.getbbox() or (0, 0, im.width, im.height))
    h = int(round(px * CAL["emoji_h_em"])); w = max(1, int(round(im.width * h / max(1, im.height))))
    return im.resize((w, h), Image.LANCZOS)

def _font(px):
    f = ImageFont.truetype(MONT, int(round(px)))
    try: f.set_variation_by_axes([CAL["weight"]])
    except Exception: pass
    return f

def render_card(text, W, H, scale=1.0, y=None):
    """RGBA layer W x H. scale 1.0 = house size (Omar's drafts use clip scale 1.0)."""
    old = (RT._emoji_img, RT._font, json.dumps(RT.PRESET))
    try:
        RT._emoji_img, RT._font = _emoji_img, _font
        R = RT.PRESET["render"]; D = RT.PRESET["default"]
        R["px_per_size_unit_per_canvas_width"] = CAL["font_px_per_W"] / D["font_size"]
        R["stroke_px_per_capcut_width_em"] = CAL["stroke_per_px"] / D["stroke_width"]; R["emoji_height_em"] = CAL["emoji_h_em"]
        return RT.render_card(text, W, H, scale=scale, y=CAL["transform_y"] if y is None else y)
    finally:
        RT._emoji_img, RT._font = old[0], old[1]; RT.PRESET.clear(); RT.PRESET.update(json.loads(old[2]))

def cards_for(problem_scenes, then_texts=None, vs="Vs... ⏰", solution="The solution 🤩"):
    """D61 rule: len(then cards) == number of problem scenes. problem_scenes: list of (t0, t1); returns card dicts."""
    n = len(problem_scenes)
    then_texts = then_texts or (["The problem... 🤕"] if n == 1 else ["Christmas 2024.. 😬", "And Christmas 2025.. 🤕", "And 2023.. 🤢"][:n])
    assert len(then_texts) == n, "one then-card per problem scene (D61)"
    return [dict(t=a, dur=round(b - a, 3), text=tx, scale=1.0) for (a, b), tx in zip(problem_scenes, then_texts)]

def check_cards(cards, problem_scenes):
    """Linter: then-card count must equal problem-scene count; no card scale other than 1.0."""
    probs = []
    n_then = sum(1 for c in cards if not c["text"].lower().startswith(("vs", "the solution", "christmas 2026", "the result")))
    if n_then != len(problem_scenes): probs.append(f"FIX {n_then} then-card(s) for {len(problem_scenes)} problem scene(s) (D61: 1 problem scene = 1 caption)")
    probs += [f"FIX card '{c['text']}' scale {c.get('scale')} != 1.0 (Omar's drafts)" for c in cards if c.get("scale", 1.0) != 1.0]
    return probs

# D73 (Omar 2026-10-19 9:37 PM PT): captions max 2 rows; sizing measured from Omar's CapCut drafts on his Mac
# (150 text segments, draft_info.json): font_size 15, line_max_width 0.82, explicit "\n" break, hook clip scale
# 0.67-0.94 (median 0.81), transform_y 0.68-0.71. Exact refs: 1010 POV hook scale 0.705 y 0.681;
# 1011 Walmart hook scale 0.908 y 0.707; 1008(3) "DON'T show this to.." scale 0.881 y 0.691.
OMAR_HOOK = dict(scale=0.81, y=0.69, max_lines=2)
def card_lines(text, scale=1.0):
    old = (RT._emoji_img, RT._font, json.dumps(RT.PRESET))
    try:
        RT._emoji_img, RT._font = _emoji_img, _font
        P = RT.PRESET; R = P["render"]; D = P["default"]
        R["px_per_size_unit_per_canvas_width"] = CAL["font_px_per_W"] / D["font_size"]
        R["stroke_px_per_capcut_width_em"] = CAL["stroke_per_px"] / D["stroke_width"]
        px = CAL["font_px_per_W"] * 1080 * scale; f = _font(px); sw = CAL["stroke_per_px"] * px
        return RT.wrap(text, f, px, sw, D["line_max_width"] * 1080 * (scale if R.get("wrap_scales") else 1))
    finally:
        RT._emoji_img, RT._font = old[0], old[1]; RT.PRESET.clear(); RT.PRESET.update(json.loads(old[2]))
def fit_card(text, scale=OMAR_HOOK["scale"], max_lines=2, min_scale=0.6):
    """Shrink scale in 0.02 steps until the card wraps to <= max_lines."""
    while len(card_lines(text, scale)) > max_lines and scale > min_scale: scale = round(scale - 0.02, 2)
    return scale
def caption_lines_gate(cards, max_lines=2):
    """cards: [(text, scale)]. BLOCK any card wrapping to more than max_lines rows (D73)."""
    bad = [(t, s, len(card_lines(t, s))) for t, s in cards if len(card_lines(t, s)) > max_lines]
    return dict(gate="CAP2", ok=not bad, level="BLOCK" if bad else "INFO", over=bad)
