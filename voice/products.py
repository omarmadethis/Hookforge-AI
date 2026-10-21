"""Product map for the customer-voice layer.

Each product key matches product_profiles/<key>.json. `match` = regexes that route a competitor
video (by its product description / title) to one of OUR products. `search` = public search
terms used for YouTube / Reddit / review collection. `pages` = our page codes (corpus page_code).
"""
import re

PRODUCTS = {
    "grinch_robe": {
        "brand": "HeatedJammies / MerryJammies", "pages": ["HJ", "MJIG"],
        "own_match": [r"robe", r"jammies"],
        "match": [r"heated.*(robe|blanket|hoodie|jacket)", r"wearable (thermal )?blanket", r"blanket (hoodie|robe)",
                  r"gingerbread.*(robe|hoodie)", r"grinch robe", r"self-heating hoodie", r"princess wearable"],
        "search": ["heated grinch robe", "heated wearable blanket robe", "heated blanket hoodie review",
                   "wearable heated blanket review", "grinch robe"],
    },
    "grinchmelt_mug": {
        "brand": "GrinchMelt", "pages": ["MJIG"], "own_match": [r"mug"],
        "match": [r"(melt|fondue|melter).*mug", r"mug.*(melt|fondue)", r"grinch mug"],
        "search": ["chocolate fondue mug tealight", "melting chocolate mug candle", "grinch mug hot cocoa"],
    },
    "merryfire": {
        "brand": "MerryFire", "pages": ["MF", "MGS", "MJIG"], "own_match": [r"fire"],
        "match": [r"fire ?pit", r"fire bowl", r"tabletop fire"],
        "search": ["tabletop fire pit review", "tabletop fire pit indoor", "portable tabletop fire bowl alcohol"],
    },
    "brickhood_mask": {
        "brand": "Brick Hood", "pages": ["BH", "MJIG"], "own_match": [r"ski mask"],
        "match": [r"balaclava", r"ski mask"],
        "search": ["smiley ski mask", "novelty balaclava snowboard", "3 in 1 balaclava review", "ski mask balaclava snowboarding"],
    },
    "merryglow_lights": {
        "brand": "MerryGlow", "pages": ["MG", "MGS"], "own_match": [r"tree lights"],
        "match": [r"(animated|led|smart).*tree lights", r"tree lights", r"christmas (ceiling |tree |aurora/santa ceiling )?projector",
                  r"tree projector", r"merryglow"],
        "search": ["animated christmas tree lights app", "smart christmas tree lights review", "christmas projector lights review"],
    },
    "jollyglow_curtain": {
        "brand": "JollyGlow", "pages": ["MC"], "own_match": [r"curtain"],
        "match": [r"curtain lights", r"window (light|projector)", r"wall light", r"balcony led"],
        "search": ["christmas curtain lights window", "animated window curtain lights christmas"],
    },
    "purrventure_carrier": {
        "brand": "PurrVenture", "pages": ["PV"], "own_match": [r"carrier"],
        "match": [r"cat (bubble )?carrier", r"carrier pouch", r"cat sleeping bag"],
        "search": ["pop up cat carrier", "cat bubble backpack carrier review"],
    },
}

def route(text):
    """Return our product key for a competitor product description, or None."""
    t = (text or "").lower()
    for k, p in PRODUCTS.items():
        if any(re.search(rx, t) for rx in p["match"]): return k
    return None

def route_own(page_code, product):
    t = (product or "").lower()
    for k, p in PRODUCTS.items():
        if page_code in p["pages"] and any(re.search(rx, t) for rx in p["own_match"]): return k
    return None

# Competitor rows whose corpus product label is wrong (checked by reading the comments). Skipped by pipeline.py.
EXCLUDE_URLS = {
    "https://www.tiktok.com/@stonebrook.home/video/7576758246338333983": "corpus labels it 'portable fire pit' but comments are about a portable TV/tablet suitcase",
}
