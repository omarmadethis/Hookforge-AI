"""D192: register every live post (Buffer 'sent' history, both orgs) in learning/footage_registry.json so MR18/MR19
(no reuse / never 2 pages / never repost) see them. Input: list_posts JSON dumps. Media cached in data/posted_media/ (gitignored)."""
import json, os, re, subprocess, sys, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "engine"))
from hookforge import master_gate as MG
PAGES = {"6ad7c7b6778b240e2f6eded2": "Jolly Glow", "6ad7c63f778b240e2f6ed4e6": "PatriotsGlow", "6ad7c63f778b240e2f6ed4e5": "PurrVentures (Buffer1)",
         "6ad7e3e8778b240e2f706dfd": "PurrVentures (Buffer2)", "6ad7d610778b240e2f6f8b6c": "TrumpGlow", "6ad7d94a778b240e2f6ffc72": "merry.jammies IG"}
LABELS = {"267d0f3b": "jollyglow_G01", "5e903e04": "purrventure_P1_pool_skim", "8358a228": "purrventure_P2_hedge_trim", "6c9911ec": "trumpglow_B3",
          "45972879": "trumpglow_A3", "d7462f5e": "purrventure_P3_leaf_rake", "bd8b0d18": "jollyglow_F06_v2", "6ad7c7cd100c30fd2be358c4": "jollyglow_combo_walmart"}
D = os.path.join(MG.REPO, "data", "posted_media")
def posts(f):
    t = open(f).read(); d = json.JSONDecoder().raw_decode(t[t.find("{"):])[0]
    return [e.get("node", e) for e in d["edges"]]
def main(files):
    out = []
    for f in files:
        for p in posts(f):
            urls = re.findall(r'https://[^"\s]+?\.mp4[^"\s]*', json.dumps(p.get("assets") or []))
            if not urls: continue
            ch = p.get("channelId") or (p.get("channel") or {}).get("id"); page = PAGES.get(ch, ch)
            u = urls[0]; key = next((v for k, v in LABELS.items() if k in u or k == p["id"]), None)
            dst = os.path.join(D, hashlib.sha1(u.split("?")[0].encode()).hexdigest()[:16] + ".mp4")
            if not os.path.exists(dst):
                r = subprocess.run(["curl", "-sfL", "--max-time", "120", "-o", dst, u])
                if r.returncode or os.path.getsize(dst) < 10000:
                    if os.path.exists(dst): os.remove(dst)
                    out.append(dict(post=p["id"], page=page, status="DOWNLOAD_FAILED", url=u[:80])); continue
            sha = MG.sha(dst); reg = json.load(open(MG.REGISTRY)) if os.path.exists(MG.REGISTRY) else {}
            vid = key or next((k for k, r in reg.items() if r.get("sha256") == sha), None) or f"post_{p['id']}"
            r = MG.register(dst, vid, page=page, caption=p.get("text"), posted=True)
            reg = json.load(open(MG.REGISTRY)); reg[vid].setdefault("buffer_posts", [])
            if p["id"] not in reg[vid]["buffer_posts"]: reg[vid]["buffer_posts"].append(p["id"])
            reg[vid]["sent_at_utc"] = reg[vid].get("sent_at_utc") or p.get("sentAt"); json.dump(reg, open(MG.REGISTRY, "w"), indent=1, ensure_ascii=False)
            out.append(dict(post=p["id"], page=page, video_id=vid, status="REGISTERED"))
    return out
if __name__ == "__main__":
    r = main(sys.argv[1:]); print(json.dumps(r, indent=0, ensure_ascii=False))
