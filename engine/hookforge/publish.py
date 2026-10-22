"""D78 - Buffer posting pipeline (PREPARE ONLY). Nothing here calls Buffer or any network.

    from hookforge import publish
    item = publish.prepare(video, caption, channel_id, service="instagram", page="PatriotsGlow", video_url=None)
    # -> runs deliver.stage + deliver.verify_staged (zero-metadata gate, hard refusal),
    #    caption gates (G10 no on-screen link rules don't apply to post text, but caption must exist / be POC-cited),
    #    writes learning/publish_queue/<id>.json with status AWAITING_OMAR_APPROVAL and a Buffer create_post payload
    #    with saveToDraft=True, mode=addToQueue.
    publish.approve(item_id, approved_by="Omar", note="...")   # only after Omar's explicit OK in chat for THIS item
    publish.ready_payload(item_id)  # returns payload ONLY if approved + file re-verified; the agent then calls
                                    # Buffer create_post itself (with Omar's approval) - this module never does.
D91 hardening: approval binds to the payload sha256 + file sha256 (any change -> re-approve); approval needs Omar's quote;
saveToDraft is forced True and re-checked; shareNow/customScheduled-now refused; Drive/Dropbox share links refused as
video_url; caption gates re-run at ready time; duplicate (same file + channel) refused; the module has NO network code and
can never set POSTED - the agent records the Buffer DRAFT id with mark_drafted() after Omar's okay.
Rules: every post waits for Omar's approval (no auto-post, D41 still disabled); never shareNow; Buffer needs a public
https video URL (a Drive share link is NOT a direct file URL) -> video_url stays None until hosting is decided.
"""
import os, json, re, hashlib, datetime
from . import deliver
from .config import REPO

QUEUE_DIR = os.path.join(REPO, "learning", "publish_queue")
STATUS_WAIT, STATUS_OK, STATUS_DRAFTED, STATUS_REJECTED = "AWAITING_OMAR_APPROVAL", "APPROVED", "BUFFER_DRAFT_CREATED", "REJECTED"
STATUS_POSTED = STATUS_DRAFTED   # back-compat alias: this module never marks anything published
BAD_HOSTS = ("drive.google.com", "docs.google.com", "dropbox.com", "icloud.com", "wetransfer.com")
def _psha(p): return hashlib.sha256(json.dumps(p, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
def _check_payload(p):
    if p.get("saveToDraft") is not True: raise NotAllowed("payload must be saveToDraft=True (draft queue only)")
    if p.get("mode") not in ("addToQueue",): raise NotAllowed(f"mode {p.get('mode')} forbidden (addToQueue drafts only)")
    if p.get("schedulingType") != "automatic": raise NotAllowed("schedulingType must stay automatic")
    for a in p.get("assets", []):
        u = (a.get("video") or {}).get("url") or ""
        if not URL_RE.match(u) or any(h in u for h in BAD_HOSTS): raise NotAllowed("video_url must be a direct public https file URL (no share links)")
URL_RE = re.compile(r"^https://\S+$")

class NotAllowed(Exception): pass

LISTING_RX = re.compile(r"(?:\b[A-Z][a-z]+\b[\s,&-]+){4,}")      # D138: 4+ consecutive Title-Case words = store listing title
LISTING_WORDS = re.compile(r"(?i)\b(with|for)\b.*\b(led|stained glass|programmable|waterproof|pcs|pack|set of|inch|ft)\b")
def is_listing(text):
    body = (text or "").split("#")[0]
    return bool(LISTING_RX.search(body) or (LISTING_WORDS.search(body) and sum(w[:1].isupper() for w in body.split()) >= 4))

def _caption_checks(caption):
    probs = []
    if caption and is_listing(caption): probs.append("listing-style caption (store product title) - use a proven hook-style caption (D138)")
    if not caption or not caption.strip(): probs.append("empty caption (F78/G22: every video ships with a proven caption)")
    if len(caption) > 2200: probs.append("caption > 2200 chars (IG limit)")
    if caption and re.search(r"(?i)\bcomment(ing|s)?\b", caption): probs.append('caption uses "Comment"; use SAY "<KEYWORD>" (F93/G23)')
    if caption and re.search(r"\{[a-z_]+\}|PLACEHOLDER", caption): probs.append("unresolved placeholder in caption (e.g. {url}: product URL still missing in config/product_urls.json)")
    return probs

def build_payload(channel_id, service, caption, video_url=None, first_comment=None):
    if service not in ("instagram", "facebook"): raise ValueError("service must be instagram|facebook")
    if not re.fullmatch(r"[a-f\d]{24}", channel_id or ""): raise ValueError("channel_id must come from Buffer list_channels")
    p = {"channelId": channel_id, "schedulingType": "automatic", "mode": "addToQueue", "saveToDraft": True, "text": caption,
         "assets": [{"video": {"url": video_url}}] if video_url else [],
         "metadata": {service: {"type": "reel"}}}
    if service == "instagram": p["metadata"]["instagram"]["shouldShareToFeed"] = True
    if first_comment: p["metadata"][service]["firstComment"] = first_comment
    return p

def prepare(video, caption, channel_id, service="instagram", page="", product="", video_url=None, first_comment=None, poc=None, suggested_slot_pt=None):
    probs = _caption_checks(caption)
    if probs: raise NotAllowed("; ".join(probs))
    from . import master_gate   # D191: publish rules (caption = approved, SAY, fresh lines, never 2 pages / repost, Omar's OK)
    sp = master_gate.load_spec(video); sp.update(caption=caption, page=page or sp.get("page"))
    try: master_gate.require(video, stage="publish", spec=sp)
    except master_gate.GateRefused as e: raise NotAllowed(str(e))
    from . import routing                    # D94: locked / unconnected / over-limit channels are refused
    try: rp = routing.assert_routable(channel_id)
    except routing.RouteRefused as e: raise NotAllowed(f"route refused: {e}")
    if rp["service"] != service: raise NotAllowed(f"{rp['name']} is a {rp['service']} channel, not {service}")
    staged = deliver.stage(video)          # raises deliver.Refused on any trace
    deliver.verify_staged(staged)
    if video_url and (not URL_RE.match(video_url) or any(h in video_url for h in BAD_HOSTS)): raise NotAllowed("video_url must be a direct public https file URL (no share links)")
    os.makedirs(QUEUE_DIR, exist_ok=True)
    sha = deliver._sha(staged)
    for o in pending():
        if o["sha256"] == sha and o["payload"]["channelId"] == channel_id and o["status"] != STATUS_REJECTED:
            raise NotAllowed(f"duplicate: this file is already queued for this channel ({o['id']})")
    iid = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-") + sha[:8] + "-" + service[:2]
    item = dict(id=iid, created=datetime.datetime.now().isoformat(timespec="seconds"), page=page, product=product,
                service=service, staged=staged, sha256=sha, caption=caption, poc=poc, status=STATUS_WAIT,
                approved_by=None, approved_at=None, needs=[] if video_url else ["video_url (public direct https host)"],
                payload=build_payload(channel_id, service, caption, video_url, first_comment),
                buffer=dict(namespace=rp["namespace"], org=rp["org"], account=rp["account"], page_key=rp["page"]), suggested_slot_pt=suggested_slot_pt)
    json.dump(item, open(os.path.join(QUEUE_DIR, iid + ".json"), "w"), indent=1, ensure_ascii=False)
    return item

def prepare_fb(video, product, channel_id, video_plan=None, page="", video_url=None, rank=0, avoid=(), suggested_slot_pt=None):
    """D93: FB reel draft whose POST caption comes from fb_caption.generate (SAY CTA, iOS emoji, audience-fit, POC).
    The traction-swap text is stored on the item so the later swap reuses the exact hashtags."""
    from . import fb_caption
    cap = fb_caption.generate(product, video_plan or {}, platform="facebook", rank=rank, avoid=avoid)
    item = prepare(video, cap["text"], channel_id, service="facebook", page=page, product=cap["product"], video_url=video_url, poc=cap["poc"], suggested_slot_pt=suggested_slot_pt)
    item["fb_caption"] = cap; item["swap_after"] = dict(views=fb_caption.SWAP_VIEWS, hour_gain=fb_caption.SWAP_HOUR_GAIN)
    _save(item); return item

def prepare_fb_all(product, files_by_page, plans_by_page=None, video_urls=None, live_counts=None, after=None):
    """D95: one approval-gated FB draft per routed page. Every page gets its OWN rendered variant (variants.py rules,
    checked first, all-or-nothing), its own fb_caption (no two pages share a caption line) and its own posting-window slot."""
    from . import routing
    r = routing.route(product, live_counts=live_counts)
    pages = [p for p in r["pages"] if p["service"] == "facebook"]
    miss = [p["page"] for p in pages if p["page"] not in files_by_page]
    if miss: raise NotAllowed(f"no per-page variant file for {miss} (fresh variant per page, variants.py)")
    extra = [k for k in files_by_page if k not in {p["page"] for p in pages}]
    if extra: raise NotAllowed(f"not routable for {product}: {extra} ({r['refused']})")
    probs = routing.check_originality({p["page"]: files_by_page[p["page"]] for p in pages}, plans_by_page)
    if probs: raise NotAllowed("originality: " + "; ".join(probs))
    from . import fb_caption, caption_variants
    plans_by_page = dict(plans_by_page or {})
    for p in pages:                          # D101: pre-built original POC caption per page when the plan has no override
        pv = caption_variants.for_page(product, p["page"])
        if pv and not (plans_by_page.get(p["page"]) or {}).get("caption_override"):
            plans_by_page[p["page"]] = dict(plans_by_page.get(p["page"]) or {}, caption_override=pv["caption"], caption_poc=pv["poc"])
    used, caps, short = [], {}, []
    for p in pages:                          # all captions first: all-or-nothing, nothing queued if one page lacks a distinct caption
        try: c = fb_caption.generate(product, (plans_by_page or {}).get(p["page"]) or {}, platform="facebook", avoid=tuple(used))
        except ValueError: short.append(p["page"]); continue
        caps[p["page"]] = c; used.append(c["caption"])
    if short: raise NotAllowed(f"no distinct proven caption left for {short}: add a caption_override (audience-fit + POC) to that page's variant plan")
    items = []
    for p in pages:
        slot = routing.next_window(p["page"], after).isoformat(timespec="minutes")
        it = prepare_fb(files_by_page[p["page"]], product, p["channel"], (plans_by_page or {}).get(p["page"]), page=p["name"],
                        video_url=(video_urls or {}).get(p["page"]), avoid=tuple(x for x in used if x != caps[p["page"]]["caption"]), suggested_slot_pt=slot)
        items.append(it)
    return dict(items=items, refused=r["refused"])

# ---------------- D95 caption swap approval flow ----------------
def _swap_dir():
    from . import fb_caption; return fb_caption.SWAP_DIR
def _swap_load(sid): return json.load(open(os.path.join(_swap_dir(), sid + ".json")))
def _swap_save(it): json.dump(it, open(os.path.join(_swap_dir(), it["id"] + ".json"), "w"), indent=1, ensure_ascii=False)

def approve_swap(sid, approved_by, approval_quote):
    if approved_by != "Omar" or not approval_quote: raise NotAllowed("only Omar, with his quoted words, can approve a caption swap")
    it = _swap_load(sid)
    if it["status"] != STATUS_WAIT: raise NotAllowed(f"{sid} is {it['status']}")
    if it.get("blocked"): raise NotAllowed(f"swap blocked: {it['blocked']}")
    probs = _caption_checks(it["new_caption"] or "")
    if probs or "PLACEHOLDER" in (it["new_caption"] or ""): raise NotAllowed("; ".join(probs) or "placeholder URL")
    it.update(status=STATUS_OK, approved_by="Omar", approval_quote=approval_quote, approved_at=datetime.datetime.now().isoformat(timespec="seconds"),
              approved_text_sha=hashlib.sha256(it["new_caption"].encode()).hexdigest()); _swap_save(it); return it

def swap_action(sid, buffer_post=None):
    """What the AGENT may do after approval: a Buffer edit_post payload when the post is still in Buffer (draft/scheduled),
    otherwise the manual/Graph instruction. This module performs nothing."""
    it = _swap_load(sid)
    if it["status"] != STATUS_OK: raise NotAllowed(f"{sid} is {it['status']} - Omar must approve first")
    if hashlib.sha256(it["new_caption"].encode()).hexdigest() != it.get("approved_text_sha"): raise NotAllowed("swap text changed after approval")
    if buffer_post is not None and str(buffer_post.get("status")) not in ("sent", "sending"):
        from . import fb_caption
        return dict(kind="buffer_edit_post", args=fb_caption.swap_buffer_payload(buffer_post, it["new_caption"]))
    return dict(kind="manual_or_graph", text=it["new_caption"], how=it["how"])

def mark_swapped(sid, how):
    it = _swap_load(sid)
    if it["status"] != STATUS_OK: raise NotAllowed("not approved")
    it.update(status="SWAPPED", swapped_how=how, swapped_at=datetime.datetime.now().isoformat(timespec="seconds")); _swap_save(it); return it

def _load(iid): return json.load(open(os.path.join(QUEUE_DIR, iid + ".json")))
def _save(it): json.dump(it, open(os.path.join(QUEUE_DIR, it["id"] + ".json"), "w"), indent=1, ensure_ascii=False)

def approve(iid, approved_by, note="", approval_quote=None):
    if approved_by != "Omar": raise NotAllowed("only Omar can approve a post")
    it = _load(iid)
    if it["status"] != STATUS_WAIT: raise NotAllowed(f"{iid} is {it['status']}, not awaiting approval")
    _check_payload(it["payload"]) if it["payload"]["assets"] else None
    it.update(status=STATUS_OK, approved_by=approved_by, approved_at=datetime.datetime.now().isoformat(timespec="seconds"), note=note,
              approval_quote=approval_quote, approved_payload_sha=_psha(it["payload"]), approved_file_sha=it["sha256"])
    _save(it); return it

def ready_payload(iid):
    it = _load(iid)
    if it["status"] != STATUS_OK: raise NotAllowed(f"{iid} is {it['status']} - Omar must approve first")
    deliver.verify_staged(it["staged"])
    if deliver._sha(it["staged"]) != it.get("approved_file_sha", it["sha256"]): raise NotAllowed("file changed after approval - re-approve")
    p = it["payload"]
    if _psha(p) != it.get("approved_payload_sha"): raise NotAllowed("payload changed after approval - re-approve")
    if not p["assets"]: raise NotAllowed("no public video_url yet")
    _check_payload(p)
    probs = _caption_checks(p.get("text", ""))
    if probs: raise NotAllowed("; ".join(probs))
    return json.loads(json.dumps(p))   # copy: caller edits can't touch the approved item

def set_video_url(iid, url):
    """Attach the hosted URL. Changes the payload, so any approval is voided and Omar must approve again."""
    if not URL_RE.match(url or "") or any(h in url for h in BAD_HOSTS): raise NotAllowed("video_url must be a direct public https file URL (no share links)")
    it = _load(iid); it["payload"]["assets"] = [{"video": {"url": url}}]; it["needs"] = []
    if it["status"] == STATUS_OK: it.update(status=STATUS_WAIT, approved_by=None, approved_at=None, approved_payload_sha=None)
    _save(it); return it

def reject(iid, note=""):
    it = _load(iid); it.update(status=STATUS_REJECTED, note=note); _save(it); return it

def mark_drafted(iid, buffer_post_id):
    """Record the Buffer DRAFT id the agent created after Omar's okay. Only from APPROVED; nothing here is ever 'published'."""
    it = _load(iid)
    if it["status"] != STATUS_OK: raise NotAllowed(f"{iid} is {it['status']} - not approved")
    it.update(status=STATUS_DRAFTED, buffer_post_id=buffer_post_id, drafted_at=datetime.datetime.now().isoformat(timespec="seconds")); _save(it); return it

def pending():
    if not os.path.isdir(QUEUE_DIR): return []
    return [json.load(open(os.path.join(QUEUE_DIR, f))) for f in sorted(os.listdir(QUEUE_DIR)) if f.endswith(".json")]


def ensure_say(text, keyword):
    """D148: every caption carries SAY "<KEYWORD>". If missing, add it after the caption line, before hashtags/link lines."""
    if not keyword or re.search(r'\bSAY\s*["“]', text): return text
    lines = text.split("\n"); first = lines[0]
    m = re.search(r"\s#", first)
    head, tail = (first[:m.start()], first[m.start():]) if m else (first, "")
    lines[0] = f'{head.rstrip()} SAY "{keyword}"{tail}'
    return "\n".join(lines)
