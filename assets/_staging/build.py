import json, os, shutil, hashlib, csv
from PIL import Image
S='/workspace/hookforge/assets/_staging'; OUT='/workspace/hookforge/assets'
A={d['i']:d for d in json.load(open(S+'/sheets/A_index.json'))}
B={d['i']:d for d in json.load(open(S+'/sheets/B_index.json'))}
def r(*a): return list(a)
# (slug,type,brand_text,clean,notes)
m={}
def setr(src,idxs,slug,typ,bt,cl,note=''):
    for i in idxs: m[(src,i)]=(slug,typ,bt,cl,note)
# ---- B
setr('B',[0],'covercruise','logo','y','n','Cover Cruise logo "Ride a brighter you"')
setr('B',[55],'covercruise','logo','y','n','Cover Cruise FB banner')
setr('B',[1],'merryglow','logo','y','n','MerryGlow wordmark + tree')
setr('B',[2,10],'merryglow','lifestyle','y','n','woman in green Grinch robe holding MerryGlow box (cross-product gift frame); box has logo')
setr('B',[3,8,9,36,46,65],'merryglow','lifestyle','n','y','AI start frame: living room with tree, "before"/setting plate')
setr('B',[6],'merryglow','lifestyle','n','y','AI start frame: man pressing wall switch')
setr('B',[15],'merryglow','product','n','n','grid of animated tree-light designs (collage)')
setr('B',[16,17,19],'merryglow','other','y','n','listing infographic (before/after, whats in the box, setup steps)')
setr('B',[20,51],'merryglow','box','y','y','MerryGlow retail box render "Make Every Tree Magical"')
setr('B',[49],'merryglow','lifestyle','y','n','POV unboxing MerryGlow box in green robe')
setr('B',[52],'merryglow','lifestyle','n','y','AI frame: green-suited figure on ladder at tree top, lights lit')
setr('B',[54],'merryglow','lifestyle','n','y','AI frame: man tangled in old lights (problem scene)')
setr('B',[56,59,61,83,85,105],'merryglow','lifestyle','n','y','AI frame: man on ladder at tree top (drop-from-top install)')
setr('B',[82],'merryglow','lifestyle','n','y','AI frame: messy room with boxes, man by tree')
setr('B',[84,86,88],'merryglow','lifestyle','n','y','AI frame: tree fully wrapped in LED strands top-to-bottom (after)')
setr('B',[87],'merryglow','lifestyle','n','y','AI frame: family + golden retriever untangling lights')
setr('B',[89],'merryglow','lifestyle','n','y','AI frame: couple plugging in')
setr('B',[78,79,80,81],'merryglow','other','y','n','MagiClaus-branded listing images (alt brand name for the same tree lights)')
setr('B',[5],'patriotglow','product','y','n','"American Pride" businessman decal artwork used for the car-door projector (politically charged, middle fingers)')
setr('B',[7,101,103],'grinch_robe','lifestyle','n','y','AI frame: robe/blanket on couch')
setr('B',[11],'heatjams','logo','y','n','"heat jams" logo, tagline Warmth, Comfort, Christmas Cheer')
setr('B',[50],'heatjams','logo','y','n','heat jams FB banner with green hooded blanket')
setr('B',[111],'heatjams','product','n','y','"grinch blanket reference" green shaggy blanket (from Drive christmas clips)')
setr('B',[21],'brickhood','product','n','y','yellow knit LEGO-head mask with goggles, grin')
setr('B',[43,44,45],'brickhood','product','n','y','BrickHood variant render (Menace / Tongue Out / Big Grin)')
setr('B',[40],'brickhood','logo','y','n','"BRICK HOODS" logo')
setr('B',[41],'brickhood','logo','y','n','"BRICK HOODS" banner')
setr('B',[22],'grinch_robe','product','n','y','two women in red+green Grinch robes (Mean One colourway)')
setr('B',[25],'grinch_robe','other','y','n','"The Mean One Heated Hooded Robe" listing screenshot')
setr('B',[53,58,109],'grinch_robe','product','y','n','heat controller with Merry Jammies logo, in hand')
setr('B',[57,108],'grinch_robe','lifestyle','n','y','POV green robe fur close')
setr('B',[60],'grinch_robe','box','y','y','Merry Jammies "The Original Heated Robe" box with robe')
setr('B',[112],'grinch_robe','box','y','y','HeatedJammies box "Stay Cozy. Stay Merry." (Drive: grinch robe box.png)')
setr('B',[63,77],'grinch_robe','lifestyle','n','y','woman in plain green wearable blanket (possibly heat jams / CozyJams item)')
setr('B',[69],'grinch_robe','lifestyle','n','y','AI frame: woman unwrapping green gift on couch')
setr('B',[91],'grinch_robe','lifestyle','n','y','AI frame: green robe on floor by tree')
setr('B',[64,104],'cozyjams','lifestyle','n','y','woman in red/green Christmas pajama set (unconfirmed: CozyJams?)')
setr('B',[23,48],'grinchmelt','product','n','y','Grinch melter mug (side / empty)')
setr('B',[24],'grinchmelt','product','n','y','Grinch melter mug with chocolate + tealight')
setr('B',[27],'grinchmelt','lifestyle','n','y','woman holding mug, white bg')
setr('B',[28],'grinchmelt','box','y','y','GrinchMelt Hot Chocolate Melt Mug box')
setr('B',[66,106],'grinchmelt','logo','y','n','GrinchyMelt logo/cover')
setr('B',[29,30,31,32,33,34,42],'merryfire','lifestyle','n','y','AI frame: MerryFire on coffee table in living room')
setr('B',[35],'merryfire','logo','y','n','MERRY FIRE logo badge')
setr('B',[37],'merryfire','other','y','n','MerryFire banner "Warm Moments, Brighter Holidays"')
setr('B',[67],'minionmask','logo','y','n','MinionMask banner "Goggles on. Mask over. Send it."')
setr('B',[68],'minionmask','logo','n','n','MinionMask round icon')
setr('B',[70,71,72,73,74,75,76],'jollyglow','lifestyle','y','n','competitor/reference frame with caption text ("The perfect Christmas decor doesnt exi-")')
setr('B',[14,26],'_unassigned','lifestyle','n','n','man in snow with plaid blanket over object (unclear product)')
setr('B',[39,90,102],'_unassigned','lifestyle','n','n','generic AI plate (empty room / hallway / POV phone)')
setr('B',[47],'_unassigned','other','n','n','snowblower with Santa decor ("WINNER_ISAACS") — product unclear')
setr('B',[110],'_unassigned','other','n','n','real photo of decorated tree (Drive christmas clips IMG_4471)')
EXCL={('B',12):'personal photo',('B',13):'personal/unrelated photo',('B',38):'Shopify robot art, unrelated'}
for i in range(92,101): EXCL[('B',i)]='CreateIt (Roblox game) art, unrelated'
# ---- A
setr('A',[0,1],'minionmask','other','n','n','banga multiplier contact sheet')
setr('A',[2],'minionmask','logo','y','n','MinionMask FB cover')
setr('A',[3,4,5],'minionmask','logo','n','n','MinionMask FB logo/pfp')
setr('A',list(range(6,26)),'minionmask','product','n','y','AI product shot on mannequin (variant per filename)')
setr('A',[26,28,29,30],'minionmask','other','n','n','Minions character IP reference — do not use in gen prompts (IP block risk)')
setr('A',[27],'minionmask','other','n','n','black/white matte mask file, not a photo')
setr('A',[31,32,33],'grinchmelt','product','n','y','mug angle (side/back), Shopify-style white bg')
setr('A',[34,41,58],'grinchmelt','product','n','y','Grinch melter mug front, white bg')
setr('A',[59],'grinchmelt','product','n','y','mug with chocolate + candle (reference)')
setr('A',[35,36,37,38],'grinchmelt','logo','y','n','GrinchyMelt FB cover')
setr('A',[39,40],'grinchmelt','logo','y','n','GrinchyMelt logo')
setr('A',[42,43,44],'grinchmelt','logo','y','n','GrinchDip alt-account cover/pfp')
setr('A',[45],'grinchmelt','box','y','y','"Greenbelt" chocolate melting mug box (IP-safe alias)')
setr('A',[46],'grinchmelt','box','y','y','GrinchMelt chocolate melting mug box')
setr('A',[47],'grinchmelt','other','y','n','"The idea" cardboard concept frame')
setr('A',[48,60],'grinchmelt','box','y','y','GreenMelt Hot Chocolate Melt Mug box')
setr('A',[49],'grinchmelt','box','y','y','GreenMelt box, art-free version')
setr('A',[57],'grinchmelt','box','y','y','GrinchMelt retail box')
setr('A',[50,61],'grinchmelt','product','n','y','fuzzy goblin mug variant (IP-safe redesign)')
setr('A',[51],'grinchmelt','other','n','n','goblin face texture ref')
setr('A',[52],'grinchmelt','other','n','n','mug + onesie collage')
setr('A',[53],'grinchmelt','other','n','n','green onesie reference collage')
setr('A',[54],'grinchmelt','lifestyle','n','y','girl holding goblin mug, white bg')
setr('A',[55,56],'grinchmelt','lifestyle','n','y','woman with mug by tree')
setr('A',[65],'merryfire','lifestyle','n','n','style ref (girl in snow), not product')
setr('A',[66],'merryfire','other','y','n','reference hook frame with caption')
setr('A',[67],'merryfire','product','n','y','white-background hero, lit')
setr('A',[68,69,70,72],'merryfire','lifestyle','n','y','pro photo scene (red studio / porch / smores / gift)')
setr('A',[71],'merryfire','product','n','y','artwork detail')
setr('A',[73],'merryfire','product','n','y','whats included (bowl, tray, smores)')
setr('A',[74,75],'merryfire','other','y','n','spec sheet infographic')
setr('A',list(range(76,85)),'merryfire','product','n','y','official product photo (hands / lighting / fuel / hero)')
setr('A',[85,86],'merryfire','box','y','y','MerryFire Tabletop Fire Bowl & Smores Set box')
setr('A',[87],'purrventure','logo','y','n','PurrVenture FB cover "Big adventures for little paws"')
setr('A',[88],'purrventure','logo','n','n','PurrVenture cat logo')
setr('A',[89,90,91],'purrventure','lifestyle','y','n','viral source frame (problem/vs/solution) with caption, 360p')
setr('A',[94],'grinch_robe','logo','y','n','Merry Jammies logo ("main logo")')
setr('A',[111],'grinch_robe','logo','y','n','Merry Jammies logo')
setr('A',[95,96],'patriotglow','other','y','n','TrumpGlow car-door projector reference review sheet (Real Madrid IP in source)')
setr('A',[100],'_unassigned','other','n','n','red Santa snowblower ("WINNER_ISAAC") — product unclear')
setr('A',[101],'grinch_robe','box','y','y','Merry Jammies red "Wrap Up the Holidays" box')
setr('A',[102],'brickhood','lifestyle','n','y','4 riders on chairlift in masks')
setr('A',[103],'brickhood','lifestyle','n','y','snowboarder snow angel in mask')
setr('A',[104,105],'merryglow','lifestyle','n','y','AI frame: man on ladder at tree top')
setr('A',[106],'grinch_robe','lifestyle','y','n','POV hands with Merry Jammies controller')
setr('A',[107],'grinch_robe','product','n','y','two women in green Grinch robes + controller, white bg (grinchrobe.png)')
setr('A',[108],'grinch_robe','product','n','y','green robe 4 views (front/side/back/3-4)')
setr('A',[109],'grinch_robe','product','n','y','red "Mean One" robe 4 views')
setr('A',[110],'merryglow','box','y','y','MerryGlow box (merryglow box.png)')
setr('A',[112],'grinch_robe','other','y','n','"The Mean One Heated Hooded Robe" listing (updated robe.png)')
setr('A',[113,114],'jollyglow','logo','y','n','jolly glow FB cover')
setr('A',[115,116],'jollyglow','logo','y','n','jolly glow profile logo')
setr('A',[117,118,119],'jollyglow','lifestyle','n','y','viral reference frame, no caption (hook / reveal / balcony)')
setr('A',[120],'jollyglow','box','y','n','supplier (Oruva) box + rolled curtain flat-lay; Oruva branding')
setr('A',[121,124],'jollyglow','lifestyle','n','y','supplier photo: balcony curtain lights in use')
setr('A',[122],'jollyglow','other','n','n','supplier dimension diagram')
setr('A',[123],'jollyglow','lifestyle','n','n','supplier collage')
DISP={'grinch_robe':'Heated Grinch robe | MerryJammies / HeatedJammies / The Mean One (red variant) / Merry Jammies Original Heated Robe',
'merryglow':'MerryGlow tree lights | Smart Animated Christmas Tree Lights (Shopify) / MagiClaus (alt listing brand)',
'merryfire':'MerryFire tabletop fire pit | MerryFire Tabletop Fire Bowl & S\'mores Set / Holiday Fire Pit & S\'mores Set',
'brickhood':'Brick Hood LEGO-head ski mask | BrickHood™ – Ski Mask / BRICK HOODS (variants Menace, Tongue Out, Big Grin, Chomp)',
'minionmask':'MinionMask yellow-character ski mask (BrickHood sub-line) | MinionMask',
'grinchmelt':'GrinchMelt chocolate melter mug | GrinchyMelt / GrinchDip / GreenMelt / Greenbelt / Grinch Chocolate Warmer Mug / Hot Chocolate Melt Mug',
'jollyglow':'JollyGlow curtain lights | jolly glow / Oruva Smart LED Balcony Christmas Lights (supplier)',
'purrventure':'PurrVenture pop-up cat carrier | PurrVenture (RollyMew Prod folder)',
'heatjams':'heat jams wearable blanket | heat jams (possibly = CozyJams, unconfirmed)',
'cozyjams':'CozyJams (unconfirmed) | Christmas pajama set frames',
'patriotglow':'PatriotGlow / TrumpGlow car-door projector | American Pride businessman decal',
'covercruise':'Cover Cruise | Cover Cruise (car cover / car brand, logo only)',
'_unassigned':'unassigned'}
rows=[]; seen={}
def add(path, srcmac, key):
    slug,typ,bt,cl,note=m[key]
    h=hashlib.md5(open(path,'rb').read()).hexdigest()
    if h in seen:
        seen[h]['notes']+=f' | dup also at {srcmac}'; return
    name=os.path.basename(path)
    if name=='main logo': name='main logo.webp'
    d=f'{OUT}/{slug}/{typ}'; os.makedirs(d,exist_ok=True)
    dst=f'{d}/{name}'
    if os.path.exists(dst): dst=f'{d}/{os.path.splitext(name)[0]}_{h[:6]}{os.path.splitext(name)[1]}'
    shutil.copy2(path,dst)
    try: w,hh=Image.open(dst).size; res=f'{w}x{hh}'
    except: res=''
    row=dict(product=DISP[slug].split(' | ')[0],slug=slug,names_aliases=DISP[slug].split(' | ')[1] if ' | ' in DISP[slug] else '',box_path=dst,source_path_mac=srcmac,type=typ,resolution=res,has_brand_text=bt,clean_for_reference=cl,notes=note,md5=h)
    rows.append(row); seen[h]=row
missing=[]
for src,idx in (('A',A),('B',B)):
    for i,d in idx.items():
        key=(src,i)
        rel=d['path'].replace(f'{S}/{src}/','')
        mac='~/'+rel
        if key in EXCL: continue
        if key not in m:
            if d['dup_of'] is not None: key2=(src,d['dup_of'])
            else: missing.append(key); continue
            m[key]=m[key2]
        add(d['path'],mac,key)
# shopify
m[('S',0)]=('merryglow','product','y','n','Shopify (MerryGlow store, merryglows.com) featured image for "Smart Animated Christmas Tree Lights", $89.95, active')
m[('S',1)]=('brickhood','product','y','n','Shopify (BrickHood store) featured image lh-product-hero.jpg for "BrickHood™ – Ski Mask", $21.99, variants Menace/Tongue Out/Big Grin/Chomp; shows box, pouch, card')
add(f'{S}/shopify/merryglow_smart-animated-christmas-tree-lights_featured.png','shopify:user-Shopify (MerryGlow) product 10309737251114',('S',0))
add(f'{S}/shopify/brickhood_ski-mask_lh-product-hero.jpg','shopify:user-Shopify--brickhood product 10889456976211',('S',1))
with open(f'{OUT}/ASSETS.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print('rows',len(rows),'missing',missing)
from collections import Counter
c=Counter((r['slug'],r['type']) for r in rows)
for k in sorted(c): print(k,c[k])
