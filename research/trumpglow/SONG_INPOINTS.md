# TrumpGlow song in-points (POC), 2026-10-19 PT
Method: the reference audio is the official Apple/iTunes 30 s preview (a legal public preview, saved in /workspace/ref). Cross-correlation used 40-band log-spectrum features at 10 ms hops, scored on 2 s windows (script: /workspace/ref/xc.py). Lyrics came from faster-whisper (small model).
Caveat: the full tracks were NOT downloaded, so a preview's position inside the full song is estimated from song structure (±5 s).

## AC/DC "You Shook Me All Night Long" (Back In Black, 3:30)
| Ad | Ad audio length | Matches preview | Section |
|---|---|---|---|
| 1535609177378226 | 18.3 s | preview 0.00 → 18.0 s, offset 0.00 s, score 0.91–0.95 on every window | "had me fighting for air / she told me to come but I was already there" → pre-chorus "walls start shaking / earth was quaking / mind was aching" → into the chorus "(you) shook me all night long" at ~14.5 s |
| 881661623891415 | 11.3 s | preview 0.00 → 11.3 s, score 0.90–0.95 | same start; ends on "my mind was aching", right before the chorus |
| 1104505214637441 | 14.1 s | preview 0.00 → ~10.5 s, then the music ends (silence or VO) | same start |
**Finding:** all 3 ads start exactly at frame 0 of the Apple preview, which is the stock "suggested clip" that platform music pickers serve. In the song this is the end of verse 1, ≈0:38 ("had me fighting for air"), with the pre-chorus at ≈0:43 and the first chorus at ≈0:52 (structure estimate).
**IN-POINT:** start at "had me fighting for air" (≈0:38, which is preview 0:00). Land the reveal on the pre-chorus "walls start shaking" (+5.5 s) and hit the chorus "you shook me all night long" at +14.5 s. TikTok/CapCut use the same chorus window (search: ~0:45–1:00).

## KALEO "Way Down We Go" (A/B, 3:39)
| Ad | Length | Result |
|---|---|---|
| 1134560391114045 | 18.9 s | Motivational voice-over ("In order to be successful... find out what makes you excited...") over a low music bed. Best preview correlation is only 0.48–0.67 with no consistent offset, so the bed does NOT sit inside the 30 s preview (the preview is the chorus "way down we go"). It's the quiet verse/intro bed under the VO |
| 772464948411145 | 18.9 s | Same audio as 1134560391114045 (identical match scores): the same creative |
**IN-POINT for our use:** the chorus "Oh, way down we go", which is the Apple preview 0:00 and the TikTok "best part" loop (often sped up + reverb). The Trump ads used the song as a quiet bed under a VO, so this is POC for the song's audience fit, not for the chorus cut. If we copy the ads exactly, use the intro/verse bed at low volume under a voice.

## Tim Brown "Sultry Blues Shuffle" (stock, 1:34)
Ads 1528952181551116 and 1391555472495329 are the same 10.0 s audio. They match preview +13.5 s → +23.5 s (score 0.80–0.83, consistent offset). Apple previews of short tracks usually start near 0:00, so the ad likely uses ≈0:13–0:24 of the track. This is a mid-shuffle groove with no vocals.

## Lynyrd Skynyrd "Free Bird"
- POC: Omar's own Trump-product reel (confirmed).
- TikTok: the official sound is a 1:00 clip used in 29 videos (50.8M total views, 1.8M avg, top 23.1M), including @trumpfansunited posts (https://toklytics.app/sound/6754028512069289985).
- Apple preview: the transition section "Lord help me, I can't change... won't you fly free bird, yeah", the last vocal line right before the slow build into the solo.
- **IN-POINT:** the famous section is the guitar-solo kick-in (album version ≈4:57; double-time run ≈5:03). The 1:00 TikTok sound covers the build plus the solo start. The Apple preview's "won't you fly, free bird" line is an alternative in-point if a vocal line should land on the reveal.

## Gaps
- The IG/FB Reels audio pages need the in-app check (logged-in). Their "use audio" start point couldn't be read from the web.
- The full-track offsets are structural estimates. To make them exact, check the Apple preview start against a licensed full copy (not done).
