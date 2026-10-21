"""Transparent rules + keyword codebook for customer-voice classification (EN + ES + a little DE/NL/FR).

Each comment gets ALL matching codes (multi-label) and one `primary` code (first match in PRIORITY).
Every code is a list of regexes; edit here, re-run `python3 voice/pipeline.py`. No black box.
Optional LLM pass: see README ("Optional LLM pass"); its labels live in private/voice/llm_labels.csv and
only ever ADD codes where the rules found none (rules stay authoritative and auditable).
"""
import re

CODES = {
    # --- questions (pre-purchase information gaps) ---
    "q_price":        [r"how much", r"\bprice\b", r"\bcost", r"\$\s*\?", r"precio", r"cu[aá]nto (cuesta|vale|sale)", r"\bpreis\b", r"combien", r"quanto (custa|é|e)\b", r"qual (o )?valor", r"\bvalor\b", r"\bprecios?\b", r"quanto\?", r"cu[aá]nto\?", r"\bhm+\b\??$"],
    "q_where_buy":    [r"\blink\b", r"where (can|do|did|could) (i|you|u) (get|buy|find|order)", r"where.*(get|buy) (it|this|one)", r"name of (the|this)", r"what('?s| is) (it|this) called",
                       r"website", r"\bwhere\b.*\?$", r"d[oó]nde (lo|la|los|las)? ?(compro|consigo|venden|compraste|encuentro)", r"\bwhere to buy", r"is (it|this) on amazon", r"tiktok shop", r"\bshop\?",
                       r"how (do|can) i (get|order|buy)", r"where i can (get|buy|find)", r"name (pls|please|plz)", r"\bname\?", r"wo kann man", r"waar (kan|koop)", r"\bd[oó]nde\b", r"\bonde\b", r"\bdove\b", r"o link", r"\bcomprar\b", r"como fa[cç]o", r"\bconsigo\b", r"venden", r"vende(m)?\b", r"informaci[oó]n", r"where\??$"],
    "q_shipping":     [r"ship(ping)? to", r"\bship\b.*\?", r"deliver", r"arrive (before|by)", r"before christmas", r"how long (does|will|to) (it )?(take|ship|get here|arrive)", r"canada|\buk\b|australia",
                       r"env[ií]o", r"llega antes", r"env[ií]an a"],
    "q_sizing":       [r"\bsize", r"\bfits?\b", r"tall\b", r"plus.?size", r"\bxl\b|\b2xl|\b3xl", r"\bkids?\b.*\?", r"\badult", r"\bmen'?s?\b.*\?", r"talla", r"how big", r"dimensions", r"how long is"],
    "q_how_it_works": [r"how (does|do) (it|this|they|you) (work|turn|charge|connect|stay|plug)", r"battery|batteries|bater[ií]a", r"\bplug", r"\busb\b", r"remote|control(ler)?", r"\bapp\b", r"rechargeable|charge",
                       r"how long (does it|will it) (last|stay|burn|heat)", r"timer", r"outdoors?\b.*\?", r"waterproof", r"wifi|bluetooth", r"c[oó]mo funciona", r"what (fuel|alcohol)", r"does it (get|stay) (hot|warm)",
                       r"can you (wash|sleep|use)", r"noisy|loud|fan noise", r"does (it|this) (heat|work|come)", r"pilas", r"se conecta"],
    "q_material_safety": [r"\bsafe", r"fire hazard", r"\bburn(s|ing)?\b.*\?", r"catch fire", r"material", r"cotton|polyester|fleece|sherpa", r"washable|\bwash\b", r"toxic", r"carbon monoxide|\bco2?\b",
                       r"smell", r"seguro", r"peligro"],
    # --- objections / scepticism ---
    "objection":      [r"\bscam", r"\bfake\b", r"\bai\b|a\.i\.|ai.generated|it'?s ai", r"overpriced|too expensive|expensive", r"not worth", r"waste of money", r"gimmick", r"\btemu\b|aliexpress|shein|dollar tree|wish\.com",
                       r"cheap(ly)? made|looks cheap", r"fire hazard|house fire|burn (the|your|my) house|dangerous|death trap", r"who (needs|asked)", r"just (use|get|buy|wear) a", r"i'?d rather", r"\blazy\b", r"\bugly\b",
                       r"won'?t last|break(s)? (in|after)", r"tripping|trip (over|on)|fall down the stairs", r"robber|rob (a|the) bank|criminal|up to no good|scared of you|gangster|uneasy", r"(i'?d|i would) just (stick|use|put)", r"microwave", r"estafa|caro|falso", r"don'?t buy", r"rip.?off", r"\bdupe\b"],
    # --- purchase intent / desire ---
    "desire":         [r"\bi (need|want) (this|that|one|it|these|two|2)", r"\bneed (this|one|it)\b", r"\bwant (this|one|it)\b", r"take my money", r"add(ed|ing)? to (my )?(cart|list|wishlist)", r"christmas list", r"wish ?list",
                       r"\b(just )?(ordered|bought|purchased)\b", r"getting (one|this|these|it)", r"gonna (buy|get)", r"i'?d (buy|get)", r"must have", r"need (it|this) for my", r"lo (quiero|necesito)", r"la (quiero|necesito)",
                       r"\bquiero\b", r"\bnecesito\b", r"\bquero\b", r"preciso (de )?(um|uma|disso)", r"\bi need\b", r"\bneed (one|two|2|a)\b", r"\bwant (one|two|a)\b", r"\bme too\b", r"perfect gift", r"for my (mom|mum|wife|husband|sister|daughter|son|grandma|boyfriend|girlfriend|dad|kids?|friend)", r"\bgift\b", r"buying (this|one|it)"],
    "skeptic":        [r"no way (that|it|this|those)|there'?s no way|doubt (it|that)|(not|n'?t) (gonna|going to) (work|melt|light|heat)|won'?t (work|melt|be that bright|heat)|would take (forever|ages)|however long|no va a (alumbrar|funcionar)|не будет|does it really|is (it|this) real\b|actually work"],
    "tag_friend":     [r"@friend"],
    # --- post-purchase complaints (buyers of this or a competing product) ---
    "complaint":      [r"\bmine (broke|stopped|didn'?t|doesn'?t|never|came|arrived)", r"stopped working", r"(didn'?t|doesn'?t|did not|does not) work", r"never (came|arrived|got)", r"\breturned\b", r"\brefund",
                       r"(i|we) (got|bought|ordered) (one|it|this).*(but|and it)", r"quality (is|was) (bad|trash|poor)", r"(doesn'?t|does not|didn'?t) (heat|get warm|light)", r"came (broken|damaged)", r"not as (shown|pictured|advertised)",
                       r"no (lleg[oó]|funciona)", r"se (rompi[oó]|da[nñ]o)", r"disappointed", r"waste"],
    "ai_callout":     [r"\bai\b|a\.i\.|ai.generated|it'?s ai|\bgenerated\b|cgi|not real|fake (video|store|shelves)|price labels|photoshop|\bia\b|inteligencia artificial"],
    "too_early":      [r"(hasn'?t|has not|isn'?t|is not|not) (even )?(been )?(halloween|thanksgiving)|literally (october|september)|so+ (super )?early|it'?s (only )?(october|september)|too early|skip(ped|ping)? (halloween|thanksgiving)|halloween (first|isn'?t|hasn'?t|yet)|ni siquiera es halloween"],
    "comparison":     [r"better than", r"\bvs\.?\b|versus", r"same as (the|my)", r"cheaper (on|at)", r"(amazon|walmart|target|temu|costco|five below|aliexpress) (has|had|sells|for)", r"(saw|seen) (it|this|these) (at|on|for)",
                       r"the one (from|at)", r"\bdupe\b", r"m[aá]s barato"],
    "humor":          [r"\blol\b|\blmao|lmfao|\bhaha|jaja|jsjs|😂|🤣|💀|😭"],
    "praise":         [r"\blove\b|\bloved\b|beautiful|cute|gorgeous|amazing|so cool|nice|pretty|awesome|obsessed|lindo|hermos|bonit|precios|me encanta|que bonito"],
    "emotional":      [r"passed away|in heaven|\bcielo\b|fallec|lost my|miss (her|him|my)|cancer|memories|grief|recuerdo"],
}
PRIORITY = ["complaint", "objection", "q_where_buy", "q_price", "q_shipping", "q_material_safety", "q_how_it_works", "q_sizing",
            "desire", "skeptic", "ai_callout", "too_early", "comparison", "tag_friend", "emotional", "humor", "praise"]
QUESTION_CODES = [c for c in CODES if c.startswith("q_")]
_C = {k: [re.compile(rx, re.I) for rx in v] for k, v in CODES.items()}

def classify(text, n_tags=0):
    t = (text or "").replace("\u2019", "'").replace("\u2018", "'")
    codes = [k for k, rxs in _C.items() if any(rx.search(t) for rx in rxs)]
    if n_tags and "tag_friend" not in codes: codes.append("tag_friend")
    # a bare question mark with no specific code = generic question
    if "?" in t and not any(c.startswith("q_") for c in codes) and len(t) < 120 and not {"humor", "objection"} & set(codes):
        codes.append("q_other")
    primary = next((c for c in PRIORITY if c in codes), "q_other" if "q_other" in codes else "other")
    return primary, codes
