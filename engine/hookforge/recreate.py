"""Recreate templates + rules from the members pass 2 (MP2-1..9, docs/evidence_members_pass2.md).
P1 WORKHORSE = the exact prompt family behind the 165K reel (d7bf7598, sibling of fb_165K "DO NOT let your wife see this"):
"Recreate 1:1 + background -> @image + product swap with hood on + caption removal". Only the realism suffix is
switched to the iPhone 12 suffix (D32). Variants rotate background / person IMAGES on a proven source video (MP2-3);
never a bare person swap (MP2-6); two-person multi-reference 3-2-1 (P3) is experiment-only (MP2-7); spoken lines are a
test variable (MP2-8). Default ONE roll; re-roll only on absurd failures (D33 wins over MP2-1, see D45).
"""
import re
from .prompts import finish

P1_TEMPLATE = (
    "Recreate <<<video_1>>> 1:1 perfectly. Do not change {pos} movements, do not change the camera angles or movements at all, "
    "There are only 3 change you are going to make.\n\n"
    "Change 1: Replace the {bg_object} and the background in <<<video_1>>> with the {bg_object} and background in <<<image_2>>>. "
    "Make sure {subj} maintains the natural way of {action} as {subj} does in <<<video_1>>>\n"
    "Change 2: Replace the {source_object} in <<<video_1>>> to the {product_name} in <<<image_1>>>.{hood_clause}\n"
    "Change 3: Remove the caption from <<<video_1>>>\n\n"
    "Other than change 1, change 2, and change 3, replicate <<<video_1>>> 1:1 perfectly.")
P1_SOURCE = "d7bf7598 (verbatim family behind fb 165K 'DO NOT let your wife see this'; sibling c30309c1)"

PERSON_SWAP_EXTRA = ("\nChange 4: Replace subject 1 in <<<video_1>>> with the person in <<<image_3>>>, keeping the {product_name} from "
                     "<<<image_1>>> exactly as it looks, worn the same way.")

def p1(product_key, source_object, bg_object="couch", action="sitting and relaxing on the couch", subj="he", pos="his",
       product_name=None, hood=True, person_swap=False):
    name = product_name or {"grinch_robe": "grinch robe"}.get(product_key, "product")
    hood_clause = " Make sure subject 1 in <<<video_1>>> is also wearing the grinch hood." if (hood and product_key == "grinch_robe") else ""
    t = P1_TEMPLATE.format(pos=pos, bg_object=bg_object, subj=subj, action=action, source_object=source_object, product_name=name, hood_clause=hood_clause)
    if person_swap:
        t = t.replace("There are only 3 change", "There are only 4 change").replace("change 2, and change 3", "change 2, change 3 and change 4")
        t = t.replace("Change 3: Remove the caption from <<<video_1>>>", "Change 3: Remove the caption from <<<video_1>>>" + PERSON_SWAP_EXTRA.format(product_name=name))
    return finish(t)

def variants(product_key, source_object, backgrounds, people=None, **kw):
    """MP2-3: same proven source choreography, rotate background (image_2) and optional person (image_3) references."""
    out = []
    for i, bg in enumerate(backgrounds):
        ps = bool(people) and i < len(people)
        out.append(dict(variant=i + 1, image_2=bg, image_3=people[i] if ps else None,
                        prompt=p1(product_key, source_object, person_swap=ps, **kw), rolls=1,
                        note="one roll; re-roll only on an absurd failure (D33/D45)"))
    return out

def check(prompt, product_key=None):
    """Recreate QA (MP2-5/6/7): caption removal stated, reference tags intact, hood clause for the robe, no bare person swap,
    multi-person multi-reference 3-2-1 flagged experiment-only."""
    p = prompt; low = p.lower(); probs = []; slot = "core"
    if "<<<video_1>>>" in p or "recreate" in low or "replicate" in low:
        if "remove the caption" not in low: probs.append("MP2-5: recreate must state 'Remove the caption'")
        tags = set(re.findall(r"<<<(video|image)_(\d)>>>", p))
        if re.search(r"(reference video from|from)\s*\.\s", p) or "<<<>>>" in p: probs.append("MP2-5: empty/broken reference tag")
        if ("image", "1") not in tags: probs.append("MP2-6: product not anchored to <<<image_1>>>")
        if product_key == "grinch_robe" and re.search(r"replace the [\w ]*robe in <<<video_1>>>", low) and "grinch hood" not in low: probs.append("MP2-5: robe recreate must say 'keep/also wearing the grinch hood'")
        if re.search(r"replace (subject|the person|the man|the woman|him|her)", low) and "<<<image_1>>>" not in p:
            probs.append("MP2-6: bare person swap without product re-anchor")
        n_img = len({t for t in tags if t[0] == "image"})
        if n_img >= 4 and re.search(r"3-2-1|one\W+two\W+three", low) and re.search(r"two (people|persons)|couple|subject 2", low):
            slot = "experiment"; probs.append("MP2-7: two-person multi-reference 3-2-1 is UNPROVEN - experiment slot only")
    return dict(problems=probs, slot=slot)
