"""D189 / F107: every on-screen card emoji must be Apple Color Emoji (iOS) art rendered by hookforge.textcards (D61).
gate_card_png(text, png, W, H): BLOCK unless the card PNG is pixel-identical to textcards.render_card (Apple PNG glyphs)
and every emoji in the text resolves to an Apple PNG in assets/emoji_apple/160. Noto / system emoji renders fail."""
import os, re
from PIL import Image, ImageChops
from . import textcards as TC
EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\uFE0F\u200D]+")
def emojis(text): return [m.group(0).replace("\uFE0F", "") or m.group(0) for m in EMOJI_RE.finditer(text or "")]
def gate_text(text):
    f = []
    for e in emojis(text):
        for ch in [c for c in e if c not in "\u200d"]:
            p = TC.apple_png(ch)
            if not (os.path.exists(p) and os.path.commonpath([p, TC.E160]) == TC.E160): f.append(f"BLOCK emoji {ch!r} has no Apple PNG (D189)")
    return f
def gate_card_png(text, png, W, H, scale=1.0):
    f = gate_text(text)
    ref = TC.render_card(text, W, H, scale=scale).convert("RGBA"); got = Image.open(png).convert("RGBA")
    if got.size != ref.size or ImageChops.difference(got, ref).getbbox() is not None:
        f.append(f"BLOCK card '{text}' was not rendered with Apple emoji (textcards.render_card) (D189)")
    return f
def render(text, W, H, path, scale=1.0):
    TC.render_card(text, W, H, scale=scale).save(path); f = gate_card_png(text, path, W, H, scale)
    if f: raise ValueError(f[0])
    return path
