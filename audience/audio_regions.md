# Audio for tier-1 audiences (US first)
Read-only on `learning/music_library.csv` (owner: music workstream). This file PROPOSES region tags and additions; nothing here changes D38 (music must be proven + niche/energy matched). Region popularity is an extra filter **inside** the D38-proven set, never a reason to use an unproven song in a core slot.

## Why audio matters for geography
- Documented: audio is a reel content signal; IG predicts audio-page clicks and "Use audio" [LEVERS S2, S3]. Reels sharing a track get clustered with other reels using it, so a track's listener geography leaks into the seed audience (mechanism plausible, geo effect = **hypothesis**).
- Documented: IG's Trending-audio list in the Professional dashboard is documented for **US professional accounts** (up to 50 tracks rising over ~3 days) → a US-sourced trending list is available for free from the app itself.

## Region evidence for our songs (charts are proof of regional popularity, not of reel performance)
| song (music_library id) | US: Billboard Holiday 100, wk 2025-12-27 [S15] | UK: Official Streaming Chart 2025-12-26 [S16] | proposed `region_skew` | note |
|---|---|---|---|---|
| Mariah Carey – All I Want For Christmas Is You (`aiwfc_intro`) | #1 (70 wks at #1) | #2 (all-time #1 most-streamed UK) | tier1_global | biggest in both; DE/AU/CA also top-5 historically |
| Wham! – Last Christmas (`last_christmas`) | #4 | **#1** (UK Christmas-season #1, 12 weeks at #1) | **UK/EU-skewed** | our most proven song (10 own hits). EU popularity means it may invite EU seed audiences: watch %US on Last Christmas reels (EXP-AUD-06) |
| Brenda Lee – Rockin' Around the Christmas Tree (`rockin_around`, unproven) | #3 | #3 | tier1_global | candidate for experiment slots (energy 4) |
| Bobby Helms – Jingle Bell Rock (not in library) | **#2** | not top-5 | **US-skewed** | PROPOSE add (energy 4, exciting/store) → experiment slot first |
| Nat King Cole – The Christmas Song (`chestnuts`, unproven) | #6 | top-40 | US-skewed | calm slot candidate (GrinchMelt) |
| Dean Martin – Let It Snow (`let_it_snow`) | #8 | top-40 | US-skewed | proven ext 12.4M (robes) |
| Kelly Clarkson – Underneath the Tree (not in library) | #7 | top-40 | US-skewed | PROPOSE add (energy 4) |
| Ariana Grande – Santa Tell Me (not in library) | #5 | top-40 | tier1_global (younger) | PROPOSE add |
| Andy Williams – Most Wonderful Time (not in library) | #9 | — | US-skewed | PROPOSE add (energy 3) |
| Michael Bublé – It's Beginning to Look… / Holly Jolly (`beginning_to_look`, `holly_jolly`) | Holiday 100 regular | UK top-40 regular | tier1_global (CA artist) | proven own |
| The Pogues – Fairytale of New York | outside top-10 | #4 | **UK/IE-only** | do NOT use on US-primary variants |
| Shakin' Stevens – Merry Christmas Everyone | absent | #5 | **UK-only** | do NOT use on US-primary variants |
| Shaggy – Mr. Boombastic (Sting/TikTok remix) (`boombastic_tiktok`) | — | — | global TikTok sound | Brick Hood; check IG US Trending dashboard before each use |
| Lynyrd Skynyrd – Free Bird (`free_bird`) | US classic-rock meme | — | US-skewed (meme) | Brick Hood |
| Darlene Love / Ronettes (`baby_please`, `be_my_baby`) | Holiday 100 regulars (US) | low UK | US-skewed | |

## Proposed procedure (weekly, Nov 1 → Dec 31; ~10 min, read-only)
1. Pull the **IG US Trending audio** list (Professional dashboard on a US pro account) and the **TikTok Creative Center top songs, region = United States**, and **Spotify "Top Songs – USA" weekly**. Save to `research/music_trends.md` (owner: Viral Research) with date.
2. From Thanksgiving week, add **Billboard Holiday 100** (published weekly late Nov–Jan) as the US holiday authority; Official Charts UK for UK variants.
3. A track qualifies as `us_trending` if it is on ≥2 of the US lists and NOT on a non-target-region top list without also charting in the US.
4. Core slots: D38-proven songs, prefer `region_skew ∈ {US-skewed, tier1_global}`. Experiment slots: US-skewed unproven tracks (Jingle Bell Rock, Underneath the Tree, Santa Tell Me).
5. Avoid on US-primary variants: UK-only tracks, Spanish/Portuguese-language tracks, regional TikTok sounds whose top creators are in non-target regions (check the audio page's top reels).

## Proposed columns for `learning/music_library.csv` (for the music owner)
`region_skew` (US-skewed | tier1_global | UK/EU-skewed | UK-only | non-target), `us_chart_evidence` (e.g. `Billboard Holiday100 #2 2025-12-27`), `ig_us_trending_date`. Then `hookforge.music` can prefer US-skewed songs in tier-1 tests without breaking D38.
