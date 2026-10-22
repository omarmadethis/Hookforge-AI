import os, re, glob, pytest
from hookforge import emoji_gate as EG, original_song as OS, gates as G
R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
def test_apple_render_passes(tmp_path):
    p = str(tmp_path / "c.png"); EG.render("The result 😍🙈", 720, 1280, p); assert EG.gate_card_png("The result 😍🙈", p, 720, 1280) == []
def test_noto_render_fails(tmp_path):
    import sys; sys.path.insert(0, os.path.join(R, "style")); import render_text
    p = str(tmp_path / "n.png"); render_text.render_card("The result 😍🙈", 720, 1280).save(p)
    assert EG.gate_card_png("The result 😍🙈", p, 720, 1280)
def test_no_direct_render_text_cards():
    bad = []
    for f in glob.glob(os.path.join(R, "engine", "hookforge", "*.py")) + glob.glob(os.path.join(R, "tools", "**", "*.py"), recursive=True):
        if f.endswith(("textcards.py", "render_text.py")): continue
        if re.search(r"render_text\.render_card\(", open(f, errors="ignore").read()): bad.append(f)
    assert not bad, f"D189: render cards via textcards/emoji_gate only: {bad}"
def test_original_song_gate():
    r = dict(slug="lumarein", reel_id="7698178513446128902")
    assert OS.gate(dict(recreate_of=r, song_key="rock_that_body", song_in_s=22.2)) == []
    assert OS.gate(dict(recreate_of=r, song_key="hey_baby", song_in_s=17.9))
    assert not G.g27_original_song(dict(recreate_of=r, song_key="mambo_no5", song_in_s=0))[0]["ok"]
