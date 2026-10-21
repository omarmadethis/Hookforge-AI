# Hookforge product asset library

Built 2026-10-19 (PT) from Omar's Mac (read-only: ~/Documents product folders, ~/Jolly Glow, ~/Downloads, the merryjammies Google Drive "vids w isaac/christmas clips") plus the two Shopify stores (read-only).
Every file is listed in `ASSETS.csv` with its Mac source path, type, resolution, brand-text flag, clean_for_reference flag, notes and md5. Files are deduped by md5; when a file appeared in more than one place, the extra locations are noted on its row.
Layout: `<slug>/{product,box,logo,lifestyle,other}/`. Most images are AI-made (Higgsfield or ChatGPT) product renders and start frames, not supplier photos. Only MerryFire `product-photos/` and JollyGlow `p1–p5` (Oruva) are supplier photos.

## Best reference images per product
| product | best refs (box paths) |
|---|---|
| Heated Grinch robe (MerryJammies / HeatedJammies) | `grinch_robe/product/grinchrobe.png.webp` (2 robes + controller, white bg) · `grinch_robe/product/grinchrobe2.png` (front/side/back/3-4) · box: `grinch_robe/box/grinch robe box.png` (HeatedJammies) or `grinch_robe/box/df9d52ad-d6b2-405f-8979-ee2b775edc76.png` (Merry Jammies Original Heated Robe) |
| MerryGlow tree lights | box: `merryglow/box/merryglow box.png` · lit tree after: `merryglow/lifestyle/hf_20260916_215623_b769b667-2331-4d9d-82e0-b6e83eaea14c.png` · ladder install: `merryglow/lifestyle/hf_20260916_040659_d3012aab-315a-4e93-b5fe-adb9c8ac699a.png` |
| MerryFire fire pit | `merryfire/product/01_white_hero.png` · `merryfire/product/06-hero-lit-b.png` · box: `merryfire/box/07-box.png` |
| Brick Hood ski mask | `brickhood/product/ChatGPT Image Sep 28, 2026 at 07_04_36 PM.png` · `brickhood/product/Unknown-8.png` (tongue-out variant) · Shopify hero with box: `brickhood/product/brickhood_ski-mask_lh-product-hero.jpg` (has text and icons) |
| MinionMask (Brick Hood sub-line) | `minionmask/product/yellow_bald_grin_v1.png` · `minionmask/product/forehead_two_eye_v1.png` · `minionmask/product/evil_purple_v3_ski_goggles.png` |
| GrinchMelt mug | `grinchmelt/product/mug_reference_with_chocolate_and_candle.png` · `grinchmelt/product/mug_reference_empty_bowl.png` · box: `grinchmelt/box/box_grinchmelt.png` (IP-safe alternatives: `greenmelt_box.png`, `box_greenbelt.png`, goblin mug `mug_onesie_goblin.png`) |
| JollyGlow curtain lights | `jollyglow/lifestyle/p2.jpg` (supplier, 550px) · `jollyglow/lifestyle/ref_s5_reveal.jpg` · supplier box: `jollyglow/box/p1.png` (Oruva branded, so not clean) |
| PurrVenture cat carrier | no clean product shot. Best are `purrventure/logo/facebook-cover.png` (shows the carrier) and `purrventure/lifestyle/00.00.jpg` (360p, captioned) |
| heat jams blanket | `heatjams/product/grinch blanket reference.png` |
| PatriotGlow / TrumpGlow projector | decal art only: `patriotglow/product/3715deca-80ec-4996-b995-c400f8a9c8fe.png` |

## Notes
- Minions character refs (`minionmask/other/`) and the Real Madrid crest in the TrumpGlow reference sheets are third-party IP. Use them for understanding only and never in generation prompts.
- `cozyjams/` (Christmas pajama frames) and `heatjams/` are tentative assignments. It isn't confirmed which of them is "CozyJams".
- Excluded on purpose: personal photos, camera-roll IMG_* files in Downloads and Drive (not opened), CreateIt/Roblox art, bank statements, rental applications, the LLC folder, Ecomstein/IMG_5172.PNG, and the Drive folder whose name has sexual content.
- Contact sheets of everything reviewed are in `_contact_sheets/`.
