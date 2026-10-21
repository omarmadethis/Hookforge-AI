"""Tier-1 audience score (ADVISORY ONLY, consistent with D35: never blocks, never changes the verdict).
Scores a plan/video 0-100 on cues hypothesised to steer early test audiences toward tier-1 markets.
Weights are PRIORS (hypothesis) and are re-fit from EXP-AUD-* results (% views US/tier-1) once n>=30 posts (D36 rules).
Usage (python):  from audience.tools.tier1_score import score; score(plan_dict)
Usage (CLI):     python3 audience/tools/tier1_score.py plan.json
plan keys used (all optional): hook_text, caption, text_cards[list[str]], prompts[list[str]], song, post_hour_pt (0-23),
                               presenter ('american_creator_real'|'american_style_ai'|'none'), collab_us_creator (bool), product_world"""
import json, re, sys
PRIORS = {  # check: (weight, evidence_label)
 'us_creator_collab': (25, 'supported (own IG: Jordan Stallion reel; mechanism documented: Collab seed audience + per-country engagement signal)'),
 'presenter_us_style': (10, 'hypothesis'),
 'us_flag_in_prompts': (10, 'hypothesis (Omar rule D24: mandatory anyway)'),
 'us_only_text_cue': (12, 'hypothesis (Target/HOA/Thanksgiving/°F/white elephant/US chains)'),
 'us_spelling': (5, 'hypothesis'),
 'no_other_region_words': (10, 'hypothesis (no mum/colour/Boxing Day/Spanish words)'),
 'us_audio': (13, 'widely-reported (audio is a documented reel signal; region popularity = Billboard/IG US trending)'),
 'us_post_window': (15, 'widely-reported + own supported-hypothesis D36 (see posting-time conflict note)'),
}
US_ONLY = r"\btarget\b|walmart|costco|home depot|lowe'?s|hobby lobby|tj ?maxx|homegoods|kohl'?s|aerie|five below|\bhoa\b|thanksgiving|friendsgiving|°f|fahrenheit|white elephant|stocking stuffer|4th of july|super ?bowl|y'all"
OTHER = r"\bmums?\b|colour|favourite|\bcosy\b|neighbour|boxing day|bonfire night|argos|tesco|asda|bunnings|navidad|feliz|regalo|natal|°c|€|£|cash on delivery|\bcod\b"
US_SPELL = r"\bmoms?\b|\bcozy\b|\bcolor\b|\bfavorite\b|\bneighbors?\b"
US_SONGS = r"all i want for christmas|mariah|jingle bell rock|rockin'? around|brenda lee|let it snow|dean martin|christmas song|nat king cole|underneath the tree|santa tell me|holly jolly|most wonderful time|boombastic|free bird"
def score(p):
    text = ' '.join([p.get('hook_text', ''), p.get('caption', '')] + list(p.get('text_cards', []))).lower()
    prompts = ' '.join(p.get('prompts', [])).lower()
    h = p.get('post_hour_pt')
    checks = {
     'us_creator_collab': bool(p.get('collab_us_creator')) or p.get('presenter') == 'american_creator_real',
     'presenter_us_style': p.get('presenter') in ('american_style_ai', 'american_creator_real'),
     'us_flag_in_prompts': bool(prompts) and all(re.search(r'american flag|us flag|u\.s\. flag', x.lower()) for x in p.get('prompts', [])),
     'us_only_text_cue': bool(re.search(US_ONLY, text + ' ' + prompts)),
     'us_spelling': bool(re.search(US_SPELL, text)),
     'no_other_region_words': not re.search(OTHER, text),
     'us_audio': bool(re.search(US_SONGS, (p.get('song') or '').lower())),
     'us_post_window': h is not None and (14 <= int(h) <= 20),  # 5-11 PM ET / 2-8 PM PT = US evening across zones
    }
    s = sum(PRIORS[k][0] for k, v in checks.items() if v)
    return {'tier1_score': s, 'advisory': True, 'checks': {k: {'pass': v, 'weight': PRIORS[k][0], 'evidence': PRIORS[k][1]} for k, v in checks.items()}}
if __name__ == '__main__':
    p = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else {'hook_text': "DON'T show this to your mom 😳❄️", 'caption': 'Get yours👉', 'song': 'Mariah Carey All I Want For Christmas Is You', 'post_hour_pt': 17, 'prompts': ['... American flag on the porch ...']}
    print(json.dumps(score(p), indent=1))
