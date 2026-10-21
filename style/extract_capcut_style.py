"""CapCut style forensics: every text element + every video/audio segment in the team's 110 CapCut drafts.
Outputs (style/): text_styles.csv, segments.csv. Private-safe: no file paths, no reel ids (only reel_key + draft folder name).
CapCut coordinates: clip.transform.{x,y} in [-1,1] relative to canvas half-size, +y = up. Text centre % from top = (1-y)/2*100.
Times are microseconds in the draft; written in seconds.
"""
import os, re, json, glob, sys
import pandas as pd
ROOT = "/workspace/team/mac/text/Movies/CapCut/User Data/Projects/com.lveditor.draft"
REPO = "/workspace/hookforge"
US = 1e6
EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\u2300-\u23FF\uFE0F\u200D\U0001F3FB-\U0001F3FF]+")

def emojis_of(t):
    import emoji as _e
    return [x["emoji"] for x in _e.emoji_list(t or "")]

def rgb_hex(c):
    if not c: return ""
    return "#%02x%02x%02x" % tuple(int(round(float(v) * 255)) for v in c[:3])

def load_join():
    e = pd.read_csv(f"{REPO}/private/edits/edits.csv")
    return {r.draft: (r.reel_key if isinstance(r.reel_key, str) else None, r.variant_of if isinstance(r.variant_of, str) else None, r.views) for r in e.itertuples()}

def main():
    join = load_join()
    paths = sorted(glob.glob(f"{ROOT}/*/draft_info.json")) + sorted(glob.glob(f"{ROOT}/.recycle_bin/*/draft_info.json"))
    trows, srows = [], []
    for p in paths:
        draft = os.path.basename(os.path.dirname(p)); recycled = ".recycle_bin" in p
        d = json.load(open(p)); m = d["materials"]
        by_id = {x["id"]: (k, x) for k, v in m.items() if isinstance(v, list) for x in v if isinstance(x, dict) and "id" in x}
        W, H = d["canvas_config"]["width"], d["canvas_config"]["height"]; dur = d["duration"] / US
        rk, var, views = join.get(draft, (None, None, None))
        texts = []
        for ti, tr in enumerate(d["tracks"]):
            for si, s in enumerate(tr["segments"]):
                kind, mat = by_id.get(s["material_id"], (tr["type"], {}))
                tt = s.get("target_timerange") or {}; st = s.get("source_timerange") or {}
                t0, td = tt.get("start", 0) / US, tt.get("duration", 0) / US
                extras = [by_id.get(x, (None, {})) for x in s.get("extra_material_refs", [])]
                anims = [a for k, x in extras if k == "material_animations" for a in x.get("animations", [])]
                clip = s.get("clip") or {}; tf = clip.get("transform") or {}; sc = clip.get("scale") or {}
                base = dict(draft=draft, recycled=recycled, reel_key=rk, variant_of=var, views=views, track=ti, seg=si,
                            t_start=round(t0, 3), t_end=round(t0 + td, 3), t_dur=round(td, 3), draft_dur=round(dur, 3), canvas=f"{W}x{H}")
                if kind == "texts":
                    c = json.loads(mat.get("content", "{}")); sty = (c.get("styles") or [{}])
                    s0 = sty[0]; strokes = s0.get("strokes") or []
                    txt = c.get("text", ""); lines = txt.split("\n")
                    y = tf.get("y", 0.0); x = tf.get("x", 0.0)
                    r = dict(base, text=txt.replace("\n", " ⏎ "), emojis="".join(emojis_of(txt)), n_emojis=len(emojis_of(txt)),
                             n_lines=len(lines), chars_per_line=json.dumps([len(l) for l in lines]), max_chars_line=max(len(l) for l in lines),
                             n_words=len(re.findall(r"[A-Za-z0-9'’]+", txt)), upper_ratio=round(sum(ch.isupper() for ch in txt) / max(1, sum(ch.isalpha() for ch in txt)), 3),
                             n_style_runs=len(sty), font_file=os.path.basename((s0.get("font") or {}).get("path", "")), font_id=(s0.get("font") or {}).get("id", ""),
                             font_name=mat.get("font_name", ""), font_title=mat.get("font_title", ""), font_resource_id=mat.get("font_resource_id", ""),
                             font_size=s0.get("size"), text_size_px_field=mat.get("text_size"),
                             fill=rgb_hex(((s0.get("fill") or {}).get("content") or {}).get("solid", {}).get("color")), text_alpha=mat.get("text_alpha"),
                             stroke_color=rgb_hex((strokes[0].get("content") or {}).get("solid", {}).get("color")) if strokes else "",
                             stroke_width=round(strokes[0].get("width"), 4) if strokes else 0.0, n_strokes=len(strokes),
                             border_color_field=mat.get("border_color"), border_width_field=round(mat.get("border_width", 0), 4),
                             has_shadow=mat.get("has_shadow"), shadow_color=mat.get("shadow_color"), shadow_alpha=mat.get("shadow_alpha"),
                             shadow_angle=mat.get("shadow_angle"), shadow_distance=mat.get("shadow_distance"), shadow_smoothing=mat.get("shadow_smoothing"),
                             bg_style=mat.get("background_style"), bg_color=mat.get("background_color"), bg_alpha=mat.get("background_alpha"),
                             bg_round_radius=mat.get("background_round_radius"), bg_width=mat.get("background_width"), bg_height=mat.get("background_height"),
                             letter_spacing=mat.get("letter_spacing"), line_spacing=mat.get("line_spacing"), alignment=mat.get("alignment"),
                             typesetting=mat.get("typesetting"), line_max_width=mat.get("line_max_width"),
                             bold=s0.get("bold", False) or (mat.get("bold_width", 0) > 0), bold_width=mat.get("bold_width"),
                             italic=s0.get("italic", False) or bool(mat.get("italic_degree")), underline=s0.get("underline", False) or mat.get("underline"),
                             style_name=mat.get("style_name", ""), preset_id=mat.get("preset_id", ""), text_preset_resource_id=mat.get("text_preset_resource_id", ""),
                             caption_template=(mat.get("caption_template_info") or {}).get("resource_id", ""),
                             text_templates=json.dumps((mat.get("combo_info") or {}).get("text_templates", [])),
                             effect_ids=";".join(x.get("effect_id", "") for k, x in extras if k in ("effects", "text_templates")),
                             anim_in="|".join(f"{a.get('name')}:{a.get('duration',0)/US:.2f}" for a in anims if a.get("type") == "in"),
                             anim_out="|".join(f"{a.get('name')}:{a.get('duration',0)/US:.2f}" for a in anims if a.get("type") == "out"),
                             anim_loop="|".join(f"{a.get('name')}" for a in anims if a.get("type") not in ("in", "out")),
                             x=round(x, 4), y=round(y, 4), pct_from_top=round((1 - y) / 2 * 100, 2), pct_from_left=round((1 + x) / 2 * 100, 2),
                             scale=round(sc.get("x", 1.0), 4), rotation=clip.get("rotation", 0.0), alpha=clip.get("alpha", 1.0),
                             keyframes=len(s.get("common_keyframes") or []), global_alpha=mat.get("global_alpha"))
                    trows.append(r); texts.append(r)
                elif kind in ("videos", "audios", "effects") or tr["type"] in ("video", "audio", "adjust", "effect", "filter"):
                    speed_mat = [x for k, x in extras if k == "speeds"]
                    fades = [x for k, x in extras if k == "audio_fades"]
                    canv = [x for k, x in extras if k == "canvases"]
                    r = dict(base, track_type=tr["type"], kind=kind, src_start=round(st.get("start", 0) / US, 3) if st else None,
                             src_dur=round(st.get("duration", 0) / US, 3) if st else None, speed=s.get("speed", 1.0),
                             speed_mode=speed_mat[0].get("mode") if speed_mat else None, curve_speed=bool(speed_mat and speed_mat[0].get("curve_speed")),
                             reverse=s.get("reverse"), volume=s.get("volume"), scale=round(sc.get("x", 1.0), 4) if sc else None,
                             x=round(tf.get("x", 0), 4) if tf else None, y=round(tf.get("y", 0), 4) if tf else None, rotation=clip.get("rotation") if clip else None,
                             flip_h=(clip.get("flip") or {}).get("horizontal") if clip else None, keyframes=len(s.get("common_keyframes") or []),
                             fade_in=fades[0].get("fade_in_duration", 0) / US if fades else 0.0, fade_out=fades[0].get("fade_out_duration", 0) / US if fades else 0.0,
                             canvas_bg=(canv[0].get("type") + ":" + str(canv[0].get("blur"))) if canv else "",
                             transition=";".join(x.get("name", x.get("effect_id", "")) for k, x in extras if k == "transitions"),
                             anims=";".join(a.get("name", "") for a in [a for k, x in extras if k == "material_animations" for a in x.get("animations", [])]))
                    if kind == "videos":
                        fn = os.path.basename(mat.get("path", "")); cr = mat.get("crop") or {}
                        hf = re.search(r"hf_\d{8}_\d{6}_[0-9a-f]{8}", fn)
                        r.update(media_type=mat.get("type"), src_w=mat.get("width"), src_h=mat.get("height"), clip_dur=round(mat.get("duration", 0) / US, 3),
                                 hf_clip=hf.group(0) if hf else "", crop_ratio=mat.get("crop_ratio"), crop_scale=mat.get("crop_scale"),
                                 cropped=not (cr.get("upper_left_x", 0) == 0 and cr.get("lower_right_x", 1) == 1 and cr.get("upper_left_y", 0) == 0 and cr.get("lower_right_y", 1) == 1))
                    elif kind == "audios":
                        nm = mat.get("name") or os.path.basename(mat.get("path", ""))
                        r.update(media_type=mat.get("type"), audio_name=re.sub(r"\s+\d+(\.mp3)$", r"\1", nm), clip_dur=round(mat.get("duration", 0) / US, 3))
                    if tr["type"] == "adjust":
                        adj = [x for k, x in extras if k == "effects"]
                        hsl = [x for k, x in extras if k == "hsl" and (x.get("hue") or x.get("saturation") or x.get("lightness"))]
                        r.update(kind="adjust", media_type="adjust", adjust=";".join(f"{x.get('type')}={round(x.get('value',0),3)}" for x in adj if x.get("type"))
                                 + (";hsl=" + ",".join(f"{h.get('hue')}/{h.get('saturation')}/{h.get('lightness')}" for h in hsl) if hsl else ""))
                    srows.append(r)
        # concurrent text layers
        for r in texts:
            r["n_text_concurrent"] = sum(1 for o in texts if o["t_start"] < r["t_end"] - 1e-3 and o["t_end"] > r["t_start"] + 1e-3)
            r["text_index"] = sorted(texts, key=lambda o: o["t_start"]).index(r)
            r["n_text_in_draft"] = len(texts)
    T = pd.DataFrame(trows); S = pd.DataFrame(srows)
    # adjustment-layer materials sit on the adjust track; resolve them from the adjust segment's own material + refs
    os.makedirs(f"{REPO}/style", exist_ok=True)
    T.to_csv(f"{REPO}/style/text_styles.csv", index=False); S.to_csv(f"{REPO}/style/segments.csv", index=False)
    print("texts", len(T), "segments", len(S), S.kind.value_counts().to_dict())

if __name__ == "__main__":
    main()
