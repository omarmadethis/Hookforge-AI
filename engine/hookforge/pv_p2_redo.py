"""D108 PurrVenture P2 payoff redo PLAN (no generation). Payoff shot only: cream Bengal rolling in the black mesh ball,
woman gardener reacting in the background. Filter-safe rewrite of P2_G3 (blocked 3x by the content filter, D82):
no body-position phrasing ("sits back on her heels"), no "inside" repetition, woman fully clothed with a task (trowel),
woman ref as an image REFERENCE only (never the start image - D82 shows the start image is what tripped the filter),
fresh start frame from refs instead of P2_SF3. Refs (new account): ball 2001b911, Bengal f14b458e (D105 crop), woman b9257835."""
from .config import ensure_suffix
from . import gates, runner, ref_gate, approval_queue

SUFFIX_NOTE = "D32 iPhone suffix appended by ensure_suffix"
MEDIA = dict(product="2001b911-3882-411b-81b7-863213a8e967", cat="f14b458e-bbb1-4ee8-870e-dc710d42d7b2", woman="b9257835-b81f-4715-9a08-a41859cdb21a")

VIDEO = ("Single shot, handheld iPhone at hip height in a sunny backyard garden. A cream snow Bengal cat with blue eyes rides in the black mesh "
         "pet ball as it rolls slowly across the lawn, paws on the mesh floor, the ball rolling as one rigid sphere. "
         "In the background a woman gardener in a sun hat, long-sleeve shirt, jeans and green gardening gloves kneels by a flower bed holding "
         "a hand trowel, turns her head and smiles at the rolling ball. Real-world physics: nothing passes through the mesh, the cat never clips "
         "through the ball or the ground. Same cream snow Bengal and same black mesh ball as the references. Native ambient garden sound only, "
         "birds and the ball on grass, no music, no added sound effects, no speech. Her eyes stay on the ball. No text on screen.")
STILL = ("Photo, handheld iPhone at hip height, sunny backyard lawn with flower beds. A cream snow Bengal cat with blue eyes in the black mesh pet "
         "ball on the grass in the foreground. In the background a woman gardener in a sun hat, long-sleeve shirt, jeans and green gardening "
         "gloves kneels by a flower bed holding a hand trowel, her eyes on the ball. No text.")

def plan():
    g = dict(id="P2_G3R", model="seedance_2_5", res="720p", dur=4, scene_type="organic", prompt=ensure_suffix(VIDEO),
             start_frame=dict(prompt=ensure_suffix(STILL)), shots=[dict(code="PAYOFF", t0=0, t1=4)], source="ai")
    p = dict(brief=dict(brief="PurrVenture P2 payoff redo (payoff shot only)", product_key="purrventure_carrier", format="F04"), gens=[g])
    p["quote"] = gates.quote(p)
    rows = gates.g4_resolution(p) + gates.g6_bans(p) + gates.g9_gaze(p) + gates.g13_motion(p) + gates.g16_models(p) + gates.g18_gen_len(p)
    p["gates"] = dict(ok=all(r["ok"] for r in rows), blocks=[r for r in rows if not r["ok"]], warns=[r for r in rows if r["level"] == "WARN"], rows=rows,
                      note="payoff-only insert: hook/song/caption/card gates (G1-G3, G7, G10-G12, G14-G15, G19-G23) apply to the P2 edit, which keeps its approved hook/cards/song")
    calls = runner.build_calls(p, MEDIA["product"], cast_media_ids=(MEDIA["cat"], MEDIA["woman"]))
    for c in calls:
        params = dict(c["params"]); params["medias"] = [m for m in params["medias"] if "{job:" not in m["value"]] + ([dict(value="<still job>", role="start_image")] if c["kind"] == "video" else [])
        ref_gate.check(params, c.get("refs"))     # F88: product + cast refs on every call
    p["calls_preview"] = [dict(step=c["step"], tool=c["tool"], expected_credits=c["expected_credits"], medias=c["params"]["medias"]) for c in calls]
    return p

STALE = "ARCHIVED_STALE: P2 v2 shipped - Omar 2026-10-20 (D141). Never requote or re-queue."
def queue():
    """D141: archived for good. Returns the refusal; writes nothing, quotes nothing."""
    return dict(id="pv_P2_payoff_redo", status="ARCHIVED_STALE", ready_for_approval=False, credits=None, why=STALE)

def _queue_legacy():
    p = plan()
    return approval_queue.queue("pv_P2_payoff_redo", "redo", p, product="purrventure_carrier", cap=35,
        why="P2 payoff was weak: P2_G3 filter-blocked 3x, used fallback from P2_G2's last frame, only 0.75 s + 0.85 s physics-clean, P2 = 8.2 s < 11.3 s (D82)",
        poc=["PurrVenture POC: RollyMew gardening-woman winners 7.6M/6.4M/5.4M (F94 cast rule, refs/purrventure/manifest.json)",
             "Omar FB 1131865399523539 ball-roll payoff (proof video)"],
        extra=dict(cost_note="quote uses config 1.0/still; gpt_image_2 2k high quoted 6.5 on get_cost -> cap 35 covers it (1 still + 28 video)",
                   filter_safety=["no body-position words", "woman ref not start image", "fresh start frame", "task + clothing described", "no 'inside' repetition"]))
