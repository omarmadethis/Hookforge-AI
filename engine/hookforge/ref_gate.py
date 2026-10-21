"""F88 / D80 HARD GATE (Omar 2026-10-20): no image or video generation without product AND cast reference images attached.
check(params, refs) -> raises RefMissing. refs = dict(product=[media_id,...], cast=[media_id,...]) (Higgsfield media ids / job ids).
Every id in refs must appear in params["medias"]. Placeholders (<...>) and empty lists fail. No override flag.
Only exception: a shot whose prompt says "no product anywhere in frame" may omit product refs (cast still required);
a shot with "no people" and "no cat/animal" may omit cast refs - both must be written in the prompt, so Omar can see why."""
import re
class RefMissing(Exception): pass
UUIDISH = re.compile(r"^[0-9a-fA-F-]{20,}$")

def check(params, refs):
    refs = refs or {}; pr = (params.get("prompt") or "").lower()
    media = {m.get("value") for m in params.get("medias") or []}
    need = []
    if "no product anywhere in frame" not in pr: need.append("product")
    if not ("no people" in pr and ("no cat" in pr or "no animal" in pr)): need.append("cast")
    for k in need:
        ids = refs.get(k) or []
        if not ids: raise RefMissing(f"{k} reference images required (F88) - none given")
        for i in ids:
            if not UUIDISH.match(str(i)): raise RefMissing(f"{k} ref {i!r} is not a real media id")
            if i not in media: raise RefMissing(f"{k} ref {i} not attached in medias")
    return True
