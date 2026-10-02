# UCSFilesManager – categories and keywords

This guide explains how UCSFilesManager decides where a sound file goes, which categories
exist, how to name files so they are sorted correctly, and how to change categories and
keywords yourself.

The complete list of categories, subcategories and keywords is in [CATALOG.md](CATALOG.md).
It is generated from the category list.

How to write FX Name, Description, Keywords, genre, BPM and key is described in
[METADATA-STYLE-GUIDE.md](METADATA-STYLE-GUIDE.md). The fixed genre list is in [GENRES.md](GENRES.md).

---

## 1. UCS in short

The [Universal Category System](https://universalcategorysystem.com) (UCS) is a shared standard
for naming and sorting sound effects. Every sound gets a **CatID** at the start of its file name:

```
DOORCreak_Old Barn Door 01.wav
└─CatID─┘
```

The CatID points to a **category** and a **subcategory**, which are also the folders the file
is moved to:

```
UCS/DOORS/CREAK/DOORCreak_Old Barn Door 01.wav
```

The category list in this project has three parts:

| Part | Content | Count |
|---|---|---|
| Official UCS | 82 categories: AIR, DOORS, WEAPONS … | 753 CatIDs |
| AI GENERATED | One subcategory per official UCS category, 10 AI-only subcategories + MISC | 92 CatIDs |
| Music production | 17 categories for instruments, loops, stems and finished tracks | 167 CatIDs |

---

## 2. How the app finds the category

The app does two things, in this order.

### Step 1: files that already have a UCS CatID

If the file name **starts with** a known CatID, the file is moved straight to the right folder
without being renamed. `SYNTHPad_warm.wav` goes straight to `SYNTH/PAD/`.

This is case sensitive: `SYNTHPad_…` is recognised, `synthpad_…` is not.

### Step 2: all other files – one point per word

1. The file name is lowercased, and spaces become `_`.
2. The name is split into words on `_`.
3. Each CatID gets **one point for every word** that is also in its keyword list.
4. The CatID with the most points wins. On a tie, the app shows a selection window.

Example: `Synth Lead Supersaw 01.wav` becomes the words `synth`, `lead`, `supersaw` and `01`.

| CatID | Matching words | Points |
|---|---|---|
| SYNTHLead | synth, lead, supersaw | **3** |
| SYNTHPad, SYNTHArp and the other SYNTH subcategories | synth, supersaw | 2 |
| VOCLLead | lead | 1 |

`SYNTHLead` wins, and the file is renamed `SYNTHLead_Synth Lead Supersaw 01_….wav`.

No points means the app can't suggest anything, and you pick from the full list.

---

## 3. Naming files so they land in the right place

- **Separate words with `_` or spaces.** `Kick_01` and `Kick 01` give the word `kick`.
  `Kick01` is one word and matches nothing.
- **A hyphen does not split words.** `hi-hat` is one word, so it is also in the keyword list.
- **Write both instrument and role.** `synth_pad` matches better than just `pad`, and
  `vocal_chop` better than just `chop`.
- **A loop of one instrument:** write the instrument and "loop", for example
  `banjo_loop_90.wav`. It then goes to BANJO (see 4.3).
- **AI-generated sounds:** include an AI word (`ai`, `elevenlabs`, `suno`, `tts` …) together with
  what the sound is, for example `AI_explosion_big.wav` or `elevenlabs dog bark.wav`.
- Numbers, key and tempo (`120`, `Amin`, `124bpm`) do no harm. They just don't score.

Check a file name before moving anything:

```
python tools/build_catalog.py --match "Vocal Chop Am 120.wav"
```

---

## 4. The categories

### 4.1 Official UCS

The 82 official categories and their keywords are unchanged from UCS. The project only adds
a few extra keywords, such as `footstep`/`footsteps` in FOOTSTEPS, and fixes two keywords whose
character encoding was broken (`Quinceañera`, `Sauté`).

### 4.2 AI GENERATED

AI sounds get their own folders with the same structure as UCS:
`AI GENERATED/EXPLOSIONS` (`AIExpl`), `AI GENERATED/ANIMALS` (`AIAnml`) and so on.
ARCHIVED is left out because it is an admin folder, not a sound type. AI sounds that don't fit
anywhere else go to `AI GENERATED/MISC` (`AIMisc`).

#### Sounds that only exist with AI

Generative AI can make sounds with no counterpart in nature or in a recording. They have their
own subcategories:

| Subcategory | CatID | What | Example file name |
|---|---|---|---|
| MORPH | `AIMorph` | One sound gradually turning into another | `ai_morph_dog_into_car` |
| HYBRID | `AIHybrid` | Two sources fused at the same time | `ai_hybrid_lion_engine` |
| TIMBRE TRANSFER | `AITimbre` | A performance re-rendered with another timbre | `timbre_transfer_voice_to_violin` |
| IMAGINARY INSTRUMENT | `AIInstr` | Instruments that don't exist | `ai_imaginary_instrument` |
| IMAGINARY WORLD | `AIWorld` | Soundscapes of places that don't exist | `ai_alien_planet_ambience` |
| IMPOSSIBLE PHYSICS | `AIPhys` | Sounds that break physics | `ai_impossible_glass_bend` |
| SURREAL | `AISurr` | Dreamlike, uncanny, liminal | `ai_surreal_dream` |
| GIBBERISH | `AIGibb` | Speech in no real language | `ai_gibberish_speech` |
| ARTIFACT | `AIArtf` | The sound of the model itself: hallucinations, metallic smearing | `ai_artifact_garbled` |
| LATENT SPACE | `AILatent` | Random generations without a prompt, latent walks | `ai_latent_walk` |

#### The keywords

The keywords of each AI subcategory are built from three parts:

1. **AI words** shared by all AI subcategories: `ai, aigen, aigenerated, ai-generated, genai,
   elevenlabs, stableaudio, audiogen, audiocraft, audioldm, texttoaudio, text2audio`.
   "generated" and "generative" are left out on purpose: generative music and procedurally
   generated sounds are not necessarily AI.
2. **Category words**, for example `explosion` and `explosions`.
3. **The words from the official subcategory names**, for example `dog`, `horse` and `rifle`.
   Three kinds of words are left out:
   - words that appear in three or more categories, such as `misc`, `impact` and `handle`
   - words that are also music keywords, such as `bass` from DESIGNED/BASS DIVE and `track` from
     SPORTS/TRACK & FIELD. Otherwise "ai_bass" would land in AI GENERATED/DESIGNED.
   - words that belong to the AI-only subcategories, such as `morph` from DESIGNED/MORPH

Two AI subcategories also have their own tool names:

| Subcategory | Tool names |
|---|---|
| AI GENERATED/MUSICAL | suno, udio, musicgen, mubert, aiva, soundraw, boomy, riffusion, lyria |
| AI GENERATED/VOICES | tts, texttospeech, voiceclone, respeecher, playht, narrator |

A normal file such as `Wood_Door_Creak.wav` gets no AI option, because it has no AI word.

**AI music and instruments:** `ai_drum_loop.wav` lands in DRUMS/LOOP, not AI GENERATED, because
"drum" and "loop" give two points while the AI word gives one. The app can't require "AI word
*and* drum word"; it can only count matches. If you know a file is AI-generated, either:
- put the CatID at the start of the name yourself (`AIMusc_drum_loop.wav`), so it is moved
  without asking, or
- include the tool name and a music word (`suno_ai_song`) and pick AI GENERATED/MUSICAL in the
  selection window

### 4.3 Music production

| Category | CatShort | Subcategories |
|---|---|---|
| DRUMS | DRM | KICK, SNARE, CLAP, SNAP, HIHAT, CYMBAL, TOM, RIM, FILL, BREAK, LOOP, TOP LOOP, MISC |
| PERCUSSION | PERC | HAND DRUM, SHAKER, TAMBOURINE, COWBELL, BLOCK, SCRAPER, TRIANGLE, ORCHESTRAL, ELECTRONIC, BODY, FOUND, SLEIGH BELL, LOOP, MISC |
| TUNED PERCUSSION | TPRC | MARIMBA, XYLOPHONE, VIBRAPHONE, GLOCKENSPIEL, CELESTA, CHIMES, BELLS, GONG, KALIMBA, STEEL DRUM, MISC |
| KEYS | KEYS | PIANO, ELECTRIC PIANO, ORGAN, CLAVINET, HARPSICHORD, MELLOTRON, MISC |
| SYNTH | SYNTH | LEAD, PAD, PLUCK, ARP, CHORD, STAB, DRONE, BELL, BRASS, STRINGS, VOICE, CHIPTUNE, MISC |
| BASS | BASS | SYNTH, 808, SUB, ELECTRIC, UPRIGHT, GROWL, MISC |
| GUITAR | GITR | ELECTRIC, DISTORTED, ACOUSTIC, NYLON, SLIDE, BANJO, UKULELE, MANDOLIN, FX, MISC |
| STRINGS | STR | VIOLIN, VIOLA, CELLO, CONTRABASS, HARP, ENSEMBLE, FX, MISC |
| BRASS | BRAS | TRUMPET, TROMBONE, FRENCH HORN, TUBA, ENSEMBLE, FX, MISC |
| WOODWINDS | WWND | FLUTE, CLARINET, OBOE, BASSOON, SAXOPHONE, FREE REED, ENSEMBLE, MISC |
| ORCHESTRA | ORCH | ENSEMBLE, HIT, MISC |
| VOCALS | VOCL | LEAD, PHRASE, RAP, CHOP, ADLIB, SHOUT, CHOIR, BACKING, SPOKEN, PROCESSED, BREATH, BEATBOX, FX, MISC |
| WORLD | WRLD | PLUCKED, BOWED, WIND, PERCUSSION, VOCAL, MISC |
| SAMPLE | SMPL | LOOP, CHOP, VINYL, FOUND SOUND, MISC |
| FX | FX | RISER, DOWNLIFTER, SWEEP, IMPACT, SUB DROP, REVERSE, NOISE, GLITCH, SCRATCH, ATMOS, MISC |
| TRACKS | TRK | CINEMATIC, CLASSICAL, SUSPENSE, AMBIENT, ELECTRONIC, HIP HOP, POP, ROCK, JAZZ & BLUES, SOUL & FUNK, FOLK & COUNTRY, WORLD, CHIPTUNE, CORPORATE, KIDS, STINGER, JINGLE, MISC |
| STEM | STEM | DRUMS, PERCUSSION, BASS, KEYS, SYNTH, GUITAR, STRINGS, BRASS, WOODWINDS, VOCALS, FX, MIX |

#### The rules behind the structure

**1. Instrument family first, then role.** Playing style (chords, riffs, distorted …) is not a
category of its own, except where it is a sample-pack convention: synth lead/pad/pluck, vocal
chop and drum loop.

**2. Family words + role words.** Every subcategory in a family has the family's words (all
SYNTH entries have `synth, synths, analog, moog, juno …`), and each subcategory adds its own.
That is what makes words pointing in different directions still land correctly:

| File name | Lands in | Because |
|---|---|---|
| `synth_bass` | BASS/SYNTH | both "synth" and "bass" are there |
| `brass_stab` | BRASS/ENSEMBLE | "brass" and "stab" |
| `vocal_chop` | VOCALS/CHOP | "vocal" and "chop" |
| `drum_stem` | STEM/DRUMS | "drum" and "stem" |
| `orchestral_track` | TRACKS/CINEMATIC | "orchestral" and "track" |

**3. Loops go with the instrument.** The subcategory says *what* is playing, not whether it is a
loop or a one-shot. The word "loop" stays in the file name, so it can still be searched for.

| File name | Lands in |
|---|---|
| `banjo_loop_90` | GUITAR/BANJO |
| `sitar loop` | WORLD/PLUCKED |
| `conga loop 100` | PERCUSSION/HAND DRUM |
| `synth_bass_loop` | BASS/SYNTH |
| `drum_loop_90` | DRUMS/LOOP |
| `top_loop_124` | DRUMS/TOP LOOP |
| `perc_loop` | PERCUSSION/LOOP |
| `melodic_loop_Am` | SAMPLE/LOOP |
| `rock_song_loop` | TRACKS/ROCK |

LOOP subcategories only exist where a loop mixes several instruments: DRUMS (LOOP and TOP LOOP),
PERCUSSION and SAMPLE. Whole songs go in TRACKS.

Exceptions that keep the rule working in practice:

- **PERCUSSION/LOOP and MISC** are the only percussion subcategories with the family words
  (`perc, percussion …`). If all had them, "perc_loop" would tie with HAND DRUM, SHAKER and the rest.
- **DRUMS/TOP LOOP** has "loop" but not the drum words, so "drum_loop" goes to DRUMS/LOOP.
- **TUNED PERCUSSION/STEEL DRUM** has "drum" (steel drum) but not "loop". Otherwise it would catch
  drum loops.

**4. No overlap with official UCS where it can be avoided.** Music vocals are `VOCALS`/`VOCL`,
while `VOICES`/`VOX` is unchanged from UCS. Foley and field recordings belong in the official
`FOLEY` and `AMBIENCE`.

The official `MUSICAL` category covers some of the same instruments, such as `MUSCWind`, `MUSCStr`
and `MUSCKeyd`. A file name with a single instrument word, such as `clarinet.wav`, therefore gets
two suggestions: WOODWINDS/CLARINET and MUSICAL/WOODWIND. Both are correct; pick the one that
fits your library.

**5. TRACKS is sorted by genre.** Each genre in [GENRES.md](GENRES.md) points to one TRACKS
subcategory, and the genre names are keywords there ("amapiano_track" lands in TRACKS/WORLD).
Names that are also instrument or sound-effect words (breakbeat, folk, industrial) are left out.
STINGER (victory, game over, level complete) and JINGLE (jingles, audio logos, idents) are the
exceptions, because short cues can be in any genre.

**6. Every family has a MISC** for what doesn't fit anywhere else.

---

## 5. Changing keywords and categories

The category list is in `catalog/` and can be opened in Numbers, Excel or a text editor:

| File | Content |
|---|---|
| `catalog/ucs_official.csv` | Official UCS with all translations |
| `catalog/custom_categories.csv` | AI GENERATED and the music categories |
| `catalog/match_tests.csv` | Test file names and where they must land |
| `catalog/genres.csv` | The genre list for the Genre and Subgenre metadata fields, with TRACKS category and typical BPM |

`data.txt`, `keywords/*.txt`, `UCS(folders).zip`, `catalog/_categorylist.xlsx`,
`docs/CATALOG.md` and `docs/GENRES.md` are **generated from the CSV files**. If you edit
`keywords/*.txt` directly, your change is overwritten the next time the list is built.

### Adding a keyword

1. Open `catalog/custom_categories.csv` (or `ucs_official.csv`).
2. Find the row and add the word to the **Synonyms - Comma Separated** column, separated by a comma.
3. Run `python tools/build_catalog.py --test`, then `python tools/build_catalog.py`.

### Keyword rules

- **Single words only.** "french horn" can never match. Write `frenchhorn` and `horn`.
- **Lowercase only.** The app lowercases the file name before comparing.
- **Plurals are not automatic.** Write both `kick` and `kicks`.
- **Accented letters are fine.** The build script automatically adds the spelling a Mac may use
  for such letters in file names, where "ó" is stored as "o" plus an accent mark. Add an ASCII
  variant as well (`cajon` next to `cajón`) for people who type without accents.
- **Words removed on purpose.** The logic reviews took these words out because they pulled
  unrelated files into one subcategory:
  - `saw`: a hand saw landed in SYNTH
  - `gate`: collided with DOORS/GATE
  - `vintage`: "vintage_synth" landed in SAMPLE/VINYL
  - `legato`/`staccato`: brass and woodwinds landed in STRINGS
  - `swell`: strings landed in BRASS
  - `bars`: "8 bars" landed in VOCALS/RAP
  - `dark`, `calm`, `action`: mood words that pulled files into TRACKS
  - `game`, `success`, `fail`: UI sounds landed in TRACKS/STINGER
  - `acoustic`, `electronic`: descriptors, not drum words
  - `slam`, `flow`, `scratching`, `digital`, `crunch`, `drill`, `grime`, `swing`, `chamber`,
    `business`: common sound-effect words (door slam, water flow, power drill, reverb chamber)
    that pulled sound effects into the music categories
- **Don't put common words on a single subcategory.** Words like `hit`, `loop` and `melody` appear
  in many file names. If such a word is on only one subcategory, it pulls in files that belong
  elsewhere. Run the tests after every change.

### Adding a subcategory

Add a row with Category, SubCategory, CatID, CatShort, Explanations and keywords. The build
script rejects the row if:

- the CatID already exists, or the category/subcategory pair is already used
- a name contains a comma (it breaks `data.txt`)
- the CatID contains a space, `_` or `-`
- the CatID doesn't start with the CatShort
- the CatID is the start of another CatID, or the other way round. The app would then move
  files that already have a UCS name to the wrong folder.
- the row has no keywords, has keywords with spaces, or has uppercase keywords
- Category or SubCategory is not uppercase

### Commands

```
python tools/build_catalog.py            # check and build everything
python tools/build_catalog.py --check    # check only
python tools/build_catalog.py --test     # run the tests in catalog/match_tests.csv
python tools/build_catalog.py --match "file.wav" "file2.wav"   # show what the app would suggest
python tools/build_docs.py               # build docs/CATALOG.md and docs/GENRES.md
python tools/build_docs.py --pdf         # also build docs/UCS-catalog.pdf (needs markdown and Chromium/Chrome)
```

The tools in `tools/` need Python 3.8 or newer (the app itself does not need Python). The build
script only uses Python's standard library. `openpyxl` is only needed for the spreadsheet
`_categorylist.xlsx`, and `markdown` only for the PDF.

### The tests

`catalog/match_tests.csv` has one line per file name: the file, the CatID it must get, and how
many options the selection window may show at most. Add a line every time you find a file name
that lands in the wrong place, fix the keywords and run `--test` until everything passes.

---

## 6. Suggesting metadata for a whole library

`tools/suggest_metadata.py` goes through every audio file in a folder (for example a drive of
sample packs) and writes a spreadsheet with a suggestion per file. It renames nothing.

| Column | Content |
|---|---|
| Path | Full path of the file |
| Pack | The pack folder (with `--pack-depth 2`: publisher / pack) |
| Confidence | `high`, `medium: …` (with the reason), `already UCS`, or `REVIEW: …` (rows highlighted) |
| CatID, Category, SubCategory | Suggested category |
| FX Name | Suggested FX Name, following the style guide (25 characters, Title Case, number) |
| Suggested File Name | `CatID_FX Name_CreatorID_SourceID_UserData`, unique in the whole library |
| Description | Draft description: what it is, loop/one-shot, bars, BPM, key, root note, AI tool |
| Genre, Subgenre | From genre names in the pack, folder or file names (music categories only) |
| BPM, Key, Root Note, Bars | Read from the file and folder names; key spelled as in the style guide |
| Keywords | Sound words from the file and folder names plus plain synonyms of the CatID, nothing already in FX Name, Description or Genre |
| Alternatives | Other CatIDs that scored the same |

```
python tools/suggest_metadata.py "/path/to/Sample Packs" -o sample-packs.xlsx --creator JLP
python tools/suggest_metadata.py file-list.txt --root "/path/to/Sample Packs" --pack-depth 2 -o sample-packs.csv
```

Instead of a folder you can pass a text file with one path per line, for example made with
`find "/path/to/Sample Packs" -type f > file-list.txt`. Use `--root` to say which folder the paths
are relative to (by default the folder they all share), and `--pack-depth 2` when the folders are
`Publisher/Pack/…`. Next to the output it writes `…-problems.csv`: every row that breaks a rule of
the style guide (FX Name length and format, file name fields, key spelling, keyword format). It
should be empty.

How it decides the category:

- File-name words count most, folder words half, the pack name a tenth. Words only one
  subcategory has ("kick") count more than words several share ("drum"); describing words
  ("open", "dist") and genre words ("jungle", "disco") count less.
- The nearest folder that names an instrument family (`Rap Vocals`, `Piano`, `Bass Hits`,
  `Synth Loops`) adds to that family, unless the file itself names another family
  (`Postcards - Bass.wav` in `Guitar Loops` is a bass).
- Genre names are taken out before scoring ("Future Bass", "Drum & Bass", "Bass House"), and so
  is the publisher's name where it is spelled out (`Overdrive Audio - Guitars - Shot 16.wav` is a
  guitar, not a distorted guitar). Pack codes such as `ZEN_`, `OPS_`, `RawCut` are ignored.
- "No Kick", "NoKick", "without hats" remove that word.
- AI GENERATED needs an AI word or tool name; TRACKS needs a track word ("full track", "song",
  not "Track 02" of a kit); STEM needs "stem", "construction kit" or "songstarter", or "full mix";
  VOCALS needs a vocal word in the path; a steel drum needs "steel"; a sub drop needs "sub",
  "boom" or an FX folder (in a kit, "Drop Lead" is the lead of the drop).
- When nothing in the file or folder names matches, the pack name decides (`Vintage Drum Breaks`,
  `Soul Jazz Piano`). A loop with no instrument at all becomes SMPLLoop.
- A loop is a file with "loop", "beat" or "groove", a tempo, bars or a key in its name, or a
  tempo in its folder name. The nearest name that says loop or one-shot decides. One-shot
  drum types (kick, clap…) stay one-shots even with the pack tempo in their name.

How it writes the names:

- FX Name: describing words first, then the instrument, then "Loop", then the number. Codes,
  producer and kit names, tempos, keys and bar counts are left out; dictionary words and words
  three or more publishers use are kept (`catalog/english_words.txt` is the word list).
- The number is the file's own number when it has one (not the tempo, not a pack volume, not a
  round-robin or variation number); names are made unique by counting up.
- The SourceID is made from the pack folder name: "Lofi Dreams" → `LOFIDREAMS`,
  "Trap Essentials Vol 2" → `TEV2`.
- Keywords: only words that describe the sound ("Ethereal", "Gritty", "Vinyl", "Tremolo"),
  never pack codes, producer names, abbreviations or words that are in more than 1 % of all files,
  plus at most a few synonyms per CatID ("Bass Drum" on a kick, "Arpeggio" on an arp). Many rows
  have no keywords: the FX Name and Description already say everything the names tell.

The suggestions come from names only; the audio is not analysed. Read the rows marked REVIEW
before renaming anything, and spot-check the rest by pack.

---

## 7. Known limitations

These are in the app itself (`UCSFilesManager.exe`). Its source code (`V37.py`) is not in the
repository, so they can't be fixed from here.

- **Only `.wav`, `.mp3`, `.flac` and `.aac` are found.** `.aif`/`.aiff` and `.ogg` are skipped,
  even though `.aif` is common in sample packs.
- **Only `_` and spaces split words.** `Kick01`, `kick-01` and `kick.01` don't become `kick`.
- **Keywords with spaces can never match.** Five official UCS keywords have this problem, and the
  build script shows them as warnings.
- **Official ROBOTS and SCIFI have "ai" as a keyword.** `ai_robot_voice.wav` can therefore get
  suggestions from both AI GENERATED and official ROBOTS.
- **Case matters for files with a UCS name.** `drmkick_01.wav` is not recognised as `DRMKick`.

---

## 8. From the first draft (`_categorylist.numbers`)

If you already renamed files with CatIDs from the first spreadsheet (`DRMKi`, `WOWIFlu` …),
`catalog/README.md` lists the new CatIDs they correspond to.
