# Category catalog

`data.txt`, `keywords/*.txt` and `UCS(folders).zip` are **generated** from the CSV files in
this folder. To add or change categories or keywords, edit the CSV (Numbers, Excel or a text
editor), then run:

```
python tools/build_catalog.py            # validate + regenerate everything
python tools/build_catalog.py --check    # validate only
python tools/build_catalog.py --match "Vocal Chop Am 120.wav"   # preview the app's suggestions
```

| File | Content |
|---|---|
| `ucs_official.csv` | The official UCS list (753 CatIDs, all translations). Keywords are this project's tuned versions. |
| `custom_categories.csv` | The extension: `AI GENERATED` + the music production categories. |
| `_categorylist.xlsx` | Both lists merged, for browsing. Generated, don't edit. |

`openpyxl` is only needed for the `.xlsx`. The rest of the script uses only the standard library.

## How the app uses the catalog (why the rules below exist)

* **Already-UCS files** are recognised with `file_name.startswith(CatID)`, walking `data.txt`
  top to bottom. A CatID that is the start of another CatID (`RAIN` / `RAINClth`) would swallow
  the longer one's files. The build puts such CatIDs last in `data.txt`, which fixes the
  official `BEEP`, `RAIN` and `WIND` (GENERAL) entries. Before this fix, `RAINClth_*`, `BEEPLofi_*`, `WINDGust_*` and similar files went to `RAIN/GENERAL`, `BEEPS/GENERAL` and `WIND/GENERAL`.
* **Other files** get a lowercase name with spaces turned into `_`, which is then split on `_`. Every
  CatID scores one point per word shared with its keyword file. The highest score wins, and ties are
  offered in the selection window. Consequences:
  * keywords must be single words: `french horn` can never match, so use `frenchhorn` and `horn`.
  * `Kick01` is one word and won't match `kick`. `Kick_01` and `Kick 01` will.
  * plurals are not automatic, so list both forms.

The build rejects custom rows that break these rules: duplicate CatIDs, a duplicate
Category/SubCategory pair, commas in names, keywords with spaces, uppercase keywords, a
CatID that doesn't start with its CatShort, or a CatID without keywords.

## AI GENERATED

The category has one subcategory per official UCS category (81 of them, plus `MISC`).
`ARCHIVED` is left out because it is an admin bucket, not a sound type. The folder is
`AI GENERATED/<UCS CATEGORY>`, for example `AI GENERATED/EXPLOSIONS` with CatID `AIExpl`.

Each AI keyword file contains:
1. AI markers shared by all AI subcategories: `ai, aigen, aigenerated, genai, generated,
   generative, elevenlabs, suno, udio, stableaudio, audiogen, audiocraft, musicgen`
2. the category's core words (`explosion`, `explosions`, ...)
3. the words from the official subcategory names (`dog`, `horse`, `rifle`...). Words that
   appear in three or more categories (`misc`, `impact`, `handle`...) are skipped.

So `AI_explosion_big.wav` or `elevenlabs dog bark.wav` lands on the AI subcategory, because the
marker gives it the extra point. A normal `Wood_Door_Creak.wav` still goes straight to `DOORCreak`.

## Music production categories

Design rules:

* **Organised by instrument family, then by role.** Playing style (chords, riffs, rhythm,
  distorted, chopped...) is not a category of its own unless it is a real sample-pack
  convention, such as synth leads, pads and plucks, vocal chops, and drum loops.
* **No overlap with official UCS.** Music vocals are `VOCALS`/`VOCL`, separate from the official
  `VOICES`/`VOX`, which is left exactly as UCS defines it. Foley and field recordings belong in the
  official `FOLEY` and `AMBIENCE` categories, so `FX` only holds music-production effects.
* **Every keyword file = family words + role words.** For example, all `SYNTH` entries contain
  `synth, synths, analog, moog, juno, ...`, and `SYNTHLead` adds `lead, leads, solo`.
  `synth_lead_saw.wav` therefore scores 2 on `SYNTHLead` and only 1 on the other SYNTH entries.
  Instrument family words also make cross-family names resolve correctly: `synth_bass` gives `BASSSynth`,
  `brass_stab` gives `BRASEns`, `vocal_chop` gives `VOCLChop` and `drum_stem` gives `STEMDrums`.
* **Every family has a `MISC`.**
* CatShorts are 2–5 letters, uppercase. CatIDs are the CatShort plus a capitalised suffix, and no
  CatID is the start of another one.

| Category | CatShort | Subcategories |
|---|---|---|
| DRUMS | DRM | KICK, SNARE, CLAP, SNAP, HIHAT, CYMBAL, TOM, RIM, FILL, BREAK, LOOP, TOP LOOP, MISC |
| PERCUSSION | PERC | HAND DRUM, SHAKER, TAMBOURINE, COWBELL, BLOCK, SCRAPER, TRIANGLE, ORCHESTRAL, ELECTRONIC, LOOP, MISC |
| TUNED PERCUSSION | TPRC | MARIMBA, XYLOPHONE, VIBRAPHONE, GLOCKENSPIEL, CELESTA, CHIMES, BELLS, GONG, KALIMBA, STEEL DRUM, MISC |
| KEYS | KEYS | PIANO, ELECTRIC PIANO, ORGAN, CLAVINET, HARPSICHORD, MISC |
| SYNTH | SYNTH | LEAD, PAD, PLUCK, ARP, CHORD, STAB, DRONE, MISC |
| BASS | BASS | SYNTH, 808, SUB, ELECTRIC, UPRIGHT, GROWL, MISC |
| GUITAR | GITR | ELECTRIC, DISTORTED, ACOUSTIC, NYLON, SLIDE, BANJO, UKULELE, MANDOLIN, MISC |
| STRINGS | STR | VIOLIN, VIOLA, CELLO, CONTRABASS, HARP, ENSEMBLE, MISC |
| BRASS | BRAS | TRUMPET, TROMBONE, FRENCH HORN, TUBA, ENSEMBLE, MISC |
| WOODWINDS | WWND | FLUTE, CLARINET, OBOE, BASSOON, SAXOPHONE, FREE REED, ENSEMBLE, MISC |
| ORCHESTRA | ORCH | ENSEMBLE, HIT, MISC |
| VOCALS | VOCL | LEAD, PHRASE, RAP, CHOP, ADLIB, SHOUT, CHOIR, BACKING, SPOKEN, PROCESSED, BREATH, MISC |
| WORLD | WRLD | PLUCKED, BOWED, WIND, PERCUSSION, VOCAL, MISC |
| SAMPLE | SMPL | LOOP, CHOP, VINYL, FOUND SOUND, MISC |
| FX | FX | RISER, DOWNLIFTER, SWEEP, IMPACT, SUB DROP, REVERSE, NOISE, GLITCH, SCRATCH, ATMOS, MISC |
| STEM | STEM | DRUMS, PERCUSSION, BASS, KEYS, SYNTH, GUITAR, STRINGS, BRASS, WOODWINDS, VOCALS, FX, MIX |

## Migrating from the first draft (`_categorylist.numbers`)

Files already renamed with a draft CatID are not recognised anymore. Rename the prefix:

| Old | New | Old | New |
|---|---|---|---|
| AIMx | AIMusc | PERCTop | DRMTop |
| AISnd | AIMisc | PERCMarimb | TPRCMarimba |
| AIWep | AIWeap | PERCTOTri | PERCTri |
| DRMKi | DRMKick | PERCTOBel, PERCTOGlock | TPRCGlock |
| DRMSn | DRMSnare | PERCTOChim | TPRCChime |
| DRMCym | DRMCymb | PERCTOXyl | TPRCXylo |
| DRMBrk | DRMBreak | PERCTOGong | TPRCGong |
| DRMClp | DRMClap | PERCTOVibr | TPRCVibe |
| STRVio | STRViolin | GITRBanj | GITRBanjo |
| STRBas | STRCbass | GITRUkul | GITRUke |
| STRCel | STRCello | GITRSitr | WRLDPluck |
| VOXSpok | VOCLSpoken | GITRRytm, GITRChrd | GITRElec / GITRAco / GITRDist |
| VOXPhras | VOCLPhrase | BASSWobl | BASSGrowl |
| VOXShou | VOCLShout | BASSConr, BASSAco | BASSUpright |
| VOXVoco | VOCLProc | BASSDist | BASSGrowl / BASSElec |
| VOXChop | VOCLChop | BRASSax | WWNDSax |
| VOXChoir | VOCLChoir | BRASClari | WWNDClarinet |
| VOXAdlib | VOCLAdlib | BRASTomb | BRASTrombone |
| VOXBrth | VOCLBreath | BRASTrump | BRASTrumpet |
| VOXWrld | WRLDVocal | BRASFren | BRASFrhorn |
| VOXFem, VOXMale, VOXMisc | unchanged, back in official VOICES | WOWIFlu | WWNDFlute |
| KEYSPino | KEYSPiano | WOWIObo | WWNDOboe |
| KEYSWurl, KEYSElec | KEYSEpiano | WOWIHar | WWNDReed |
| KEYSOrg | KEYSOrgan | WOWIEns | WWNDEns |
| KEYSArp | SYNTHArp | WOWIBas | WWNDBassoon |
| KEYSChrd | KEYSPiano / KEYSEpiano | WOWIBagp | WRLDWind |
| KEYSChop, SYNTHChop | SMPLChop | WODWDMisc | WWNDMisc |
| SMPLChrd | SMPLLoop | SYNTHBass | BASSSynth |
| SMPLRaw | SMPLFound | SYNTHPluk | SYNTHPluck |
| SMPLVin | SMPLVinyl | SYNTHChrd | SYNTHChord |
| PERCDjem, PERCBong, PERCCong, PERCUdu | PERCHand | SYNTHText | SYNTHDrone |
| PERCCow | PERCCowb | SYNTHAna, SYNTHModlr | SYNTHMisc (or the role: Lead, Pad...) |
| PERCGuir | PERCScrp | SYNTHGitr, SYNTHWodwd, SYNTHBras, SYNTHKey | the role: SYNTHLead, SYNTHPad... |
| PERCClav | PERCBlock | SYNTHFx | FX* (the matching FX type) |
| PERCmisc | PERCMisc | STEMStri | STEMStrings |
| PERCDigi | PERCElec | STEM (woodwind) | STEMWwnd |
| PERCTimp | PERCOrch | STEMGitr | STEMGuitar |
| PERCMal | TPRCMisc | STEMPrc | STEMPerc |
| PERCBell | TPRCBell | FXNois | FXNoise |
| FXSwep | FXSweep | FXRise | FXRiser |
| FXImpct, FXImp | FXImpact | FXText | FXAtmos |
| FXScrach | FXScratch | FXBass | FXSubdrop |
| FXFoly, FXFol | official FOLEY (FOLYProp, FOLYHand...) | FXField, FXRec | official AMBIENCE, or SMPLFound |

`AIMech`, `AIVox`, `AIWatr`, `AIMisc` and the IDs not listed above keep their names. `AIMech` now
means AI GENERATED/MECHANICAL.
