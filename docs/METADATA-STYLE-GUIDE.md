# UCS Music – metadata style guide

How to write the file name, FX Name, Description, Keywords, genre and musical information (BPM
and key) for sounds in the music categories: DRUMS, SYNTH, VOCALS, TRACKS, STEM and the rest.
The same rules apply to AI GENERATED.

> **Basis.** This guide follows the UCS specification for file names and fields, and common
> practice in commercial sound and sample libraries. The A Sound Effect style guide
> (asoundeffect.com/metadata-style-guide) was not reachable when this guide was written, so it is
> **not checked against it**. Differences from it should be corrected here.

---

## 1. The fields that describe a sound

| Where | Field | What it is for | Example |
|---|---|---|---|
| File name | **CatID** | Sorts the file into the right folder | `SYNTHLead` |
| File name | **FX Name** | Short title, read in a file list | `Saw Lead Riff 03` |
| Metadata | **Description** | The full description; what people search and read | `Bright detuned saw lead playing a syncopated riff…` |
| Metadata | **Keywords** | Words that aren't in the Description but people will search for | `Supersaw, Festival, Anthem` |
| Metadata | **Genre** | Main genre from the fixed list | `Trance & Hard Dance` |
| Metadata | **Subgenre** | Subgenre from the fixed list | `Trance` |

Music adds **BPM**, **Key**, **Bars** and **Time Signature**.

**Language:** write all metadata in **English**. Search tools, the UCS catalog and customers use
English.

---

## 2. The file name

The UCS file name has fixed fields, separated by underscores:

```
CatID_FX Name_CreatorID_SourceID_UserData.wav
```

| Field | Rule | Example |
|---|---|---|
| CatID | Exactly as in the catalog, same upper and lower case | `BASS808` |
| FX Name | Short title. See chapter 3. | `Long Distorted 808 01` |
| CreatorID | Who made the sound: initials or a short name | `JLP` |
| SourceID | The library or project, short and uppercase | `TRAPKIT` |
| UserData | Musical information: BPM, key or root note | `140bpm Fmin` |

**Rules for the whole file name**

- **Underscores separate fields and must not be used inside a field.** Use spaces inside FX Name.
  - Right: `Saw Lead Riff 03`
  - Wrong: `Saw_Lead_Riff_03`, because every UCS tool will then read "Lead" as the CreatorID.
- **Only the letters A–Z, digits, spaces and hyphens.** No accented letters, `/`, `#`, `&`,
  `( )`, `?` or `*`.
  - File names with special characters can change between Mac and Windows, or break in zip
    files and cloud services.
  - For `#` in keys, write `Csharp` or `Db` in the file name, and `C#` in metadata.
- **Numbering:** two digits at the end of FX Name, preceded by a space: `01`, `02` … `99`.
  The number separates variations of the same sound. It is not a version number.
- **No dates, "final", "v2", "new" or "copy"** in file names that are published.

**Examples**

```
DRMKick_Punchy Acoustic Kick 04_JLP_LIVEKIT.wav
DRMLoop_Funky Break Loop 01_JLP_SPACEDRUMS_96bpm.wav
SYNTHLead_Saw Lead Riff 03_JLP_NEONPACK_124bpm Fmin.wav
BASS808_Long Distorted 808 01_JLP_TRAPKIT_C1.wav
GITRBanjo_Bluegrass Roll Loop 02_JLP_PORCH_120bpm G.wav
VOCLChop_Airy Female Chop 07_JLP_VOXPACK_128bpm Amin.wav
TRKCine_Rise Of The North Full_JLP_NORDICSCORE_100bpm Dmin.wav
AIMorph_Dog Bark Into Car Horn 01_JLP_AILAB.wav
```

### In UCSFilesManager

The app puts the CatID in front and uses the original file name as FX Name. So:

1. **Clean up the file name before running the app**, so it already is a good FX Name
   (chapter 3). The app removes `(` and `)`, but fixes nothing else.
2. In **UCS Custom Format**, write the rest of the name, for example `$filename_JLP_NEONPACK`.
3. Add BPM and key yourself, either at the end of the original file name or afterwards.

The app writes **only the file name**. Description, Keywords, Genre, BPM and Key have to be
written into the file's metadata (BWF/iXML) with a separate tool, such as Soundminer, BaseHead
or Reaper.

---

## 3. FX Name

FX Name is the title you see in a file list. It should be readable in one second.

**Rules**

- **25 characters at most**, as UCS recommends. The number counts.
- **Capitalise every word** (Title Case): `Warm Rhodes Chords 02`
- **Order:** `[Character] [Source/instrument] [Role/action] [Loop] [Number]`
  - `Tight Snare 03`
  - `Dusty Rhodes Loop 02`
  - `Airy Female Vocal Chop 07`
- **Write `Loop` in the FX Name of every loop.** Loops share the instrument folder with one-shots
  (BANJO, PIANO …), so the word "Loop" is what tells them apart.
- **No BPM, key or time signature in FX Name.** They belong in UserData and metadata.
- **Don't repeat the CatID if you need the space.** In `DRMKick`, "Kick" is already said. Write it
  anyway if there is room: the name should be readable without the CatID.
- **No internal codes or abbreviations** only you understand. `Rhodes` is fine, `RHD_MK1` is not.

| Bad | Good | Why |
|---|---|---|
| `kick_final_v2` | `Punchy Kick 02` | no version, Title Case, spaces |
| `Lead 124bpm Fmin` | `Saw Lead Riff 03` | BPM and key belong in UserData |
| `Synth Thing` | `Wobbly Pluck Arp 01` | says what it is |
| `Beautiful Emotional Cinematic Piano Chords` | `Soft Piano Chords 04` | under 25 characters; mood belongs in Description |

---

## 4. Description

Description is the field that is searched and read, and the most important field after CatID.

**Rules**

- **One to three sentences in English, in sentence case, ending with a full stop.**
- **Most important first.** Many tools only show the first 60–80 characters.
- **Fixed order:**
  1. **What:** source or instrument and role. "Warm Rhodes electric piano playing a slow chord progression."
  2. **How:** character, playing technique and development. "Soft attack, tremolo, swells in the last bar."
  3. **Musical:** BPM, key, bars and time signature. "4 bars, 90 BPM, D minor, 4/4."
  4. **Source/technique**, when useful: instrument model, microphone, amp and processing.
     "Fender Rhodes Mk I through a Fender Twin, close mic."
- **Describe what you hear, not what you feel.** "Bright, detuned, fast attack" is good.
  "Amazing, epic, insane" is not.
- **No marketing**, no "perfect for …" and no emojis.
- **Sung or spoken words** go in quotes, and the language is named:
  `Female vocal phrase singing "hold me closer" in English.`
- **Repeating words from FX Name is fine.** The Description must make sense on its own.

**Examples**

| File | Description |
|---|---|
| Kick | `Punchy acoustic kick drum, short decay with a tight beater click. Ludwig 22" kick, inside and outside mic blended.` |
| Drum loop | `Funky breakbeat drum loop with ghost notes on the snare and open hi-hats. 2 bars, 96 BPM, 4/4. Vintage-style compression.` |
| Synth lead | `Bright detuned saw lead playing a syncopated riff with portamento. 8 bars, 124 BPM, F minor, 4/4. Serum, light chorus and delay.` |
| 808 | `Long distorted 808 bass with pitch glide down at the end. Root note C1, one-shot, 3 seconds.` |
| Banjo loop | `Bluegrass banjo playing a fast forward roll pattern. 4 bars, 120 BPM, G major, 4/4. Five-string banjo, close mic.` |
| Vocal chop | `Airy female vocal chop, pitched "ah" with reverb tail. 1 bar, 128 BPM, A minor. Female, English.` |
| Track | `Epic orchestral cinematic track with Nordic folk elements: Hardanger fiddle, low brass and taiko. Builds from a quiet intro to a full climax. 100 BPM, D minor, 2:34, full mix.` |
| Stem | `Drum stem from "Rise Of The North": taiko, toms and cymbal swells. 100 BPM, D minor, 2:34.` |
| AI | `AI-generated morph of a dog bark turning into a car horn. Generated with [tool, model and version]. Prompt: "dog bark morphing into a car horn".` |

---

## 5. Keywords

Keywords are for words people will search for that are **not** in FX Name or Description.

**Rules**

- **Comma-separated, in Title Case like UCS:** `Supersaw, Festival, Anthem`
- **5–20 words.** More words give worse search results, not better.
- **Include** synonyms (`Uplifter` for Riser), instrument names and models (`Juno`, `Rhodes`, `808`),
  mood (`Dark`, `Uplifting`), playing technique and articulation (`Pizzicato`, `Palm Mute`)
  and common spellings (`Hi-Hat, Hihat, Hat`).
- **Don't include** genre, BPM, key, CreatorID, SourceID or file format. They have their own fields.
- **Don't repeat words** from FX Name and Description. They are searched anyway.
- **No keyword stuffing.** Every word must be true for this exact sound.

**Example for the synth lead**

```
Supersaw, Festival, Anthem, Hook, Melody, Detuned Saw, Euphoric
```

> Don't confuse this field with `keywords/*.txt` in UCSFilesManager. Those files are used by the
> app to *find* the CatID and have their own rules: single words and lowercase. See
> USER-GUIDE.md. The Keywords metadata field can hold multi-word terms such as `Palm Mute`.

---

## 6. Musical information

### BPM

- Whole numbers: `124`. Use decimals only when the tempo really is that: `92.5`.
- In the file name (UserData), write `124bpm` in lowercase without a space.
  In metadata, the BPM field holds just the number, and the Description says `124 BPM`.
- **Loops must loop seamlessly and be a whole number of bars** at the stated BPM.
- One-shots get no BPM.

### Key

One fixed spelling for all 24 keys:

| Major | Minor |
|---|---|
| C, G, D, A, E, B, F#, Db, Ab, Eb, Bb, F | Amin, Emin, Bmin, F#min, C#min, G#min, Ebmin, Bbmin, Fmin, Cmin, Gmin, Dmin |

- **Major is just the note:** `G`. **Minor adds `min`:** `Amin`. Not `Am`, `A minor` or `a`.
- **Use the same name for the same note**, as in the table: `F#`, `Db`, `Ab`, `Eb` and `Bb`.
  Never write `A#` where the table says `Bb`.
- In **file names**, write `#` as `sharp`: `F#min` becomes `Fsharpmin`. In metadata, write `F#min`.
- In the Description, write the key in full: `F sharp minor`, `D major`.
- **Atonal material** (noise, percussion, FX) gets no key.

### Root note for one-shots

Bass, 808, synth and instrument notes that are a single pitch get a **root note with octave**:
`C1`, `F#2`, `A3`.

- **Use scientific pitch notation: `C4` is middle C (261.6 Hz) and `A4` is 440 Hz.** Ableton and
  some other DAWs call middle C `C3`, so the library documentation must say which convention is used.
- A tuned kick or tom can get a root note. An untuned kick does not.

### Bars and time signature

- In the Description: `4 bars, 4/4`. The time signature never goes in the file name, because `/`
  is not allowed in file names.
- State the time signature either only when it isn't 4/4, or always. Pick one rule for the whole library.

---

## 7. Genre (Genre and Subgenre)

Genre has **two metadata fields of its own**: `Genre` and `Subgenre`. Both are chosen from the
fixed list in [GENRES.md](GENRES.md), which is generated from `catalog/genres.csv`. The list has
17 main genres and about 130 subgenres, with typical BPM and the TRACKS category each belongs to.

| Main genres |
|---|
| Hip Hop · R&B & Soul · Pop · House · Techno · Trance & Hard Dance · Dance & EDM · Bass Music · Electronic · Rock · Jazz & Blues · Folk & Country · Latin & Caribbean · Afro · Global · Cinematic · Classical |

**Rules**

- **Genre: exactly one main genre** from the list.
- **Subgenre: none, one or two subgenres** from the list, separated by a semicolon:
  `UK Drill` or `UK Drill; Grime`.
  - The first must belong to the main genre.
  - The second may come from another main genre when the sound is a crossover.
- **Leave Subgenre empty** when the sound is just "general" in its main genre, such as plain pop or
  rock. That is why the list has no subgenre called "Pop" or "Rock".
- **Spell names exactly as in the list:** same case, `&` and hyphens.
  `Drum & Bass`, not `DnB` or `Drum and Bass`. `Lo-Fi Hip Hop`, not `lofi`.
- **Don't invent new genres in the field.** If a genre is missing, add it to `catalog/genres.csv`
  (with main genre, TRACKS category, typical BPM and a short description) and run
  `python tools/build_catalog.py --check`.
- **Genre doesn't go in the file name or in Keywords.** It has its own field. Do mention it
  naturally in the Description when it describes the sound: "UK drill beat with sliding 808s".

**These are not genres** and go in Keywords or the Description instead:

| Type | Examples | Where |
|---|---|---|
| Performance | `Live Instruments`, `Acoustic`, `Unplugged` | Keywords |
| Mood | `Dark`, `Happy`, `Uplifting`, `Melancholic` | Keywords |
| Use | `Corporate`, `Kids`, `Vlog`, `Podcast` | Keywords. For whole tracks the CatID can be TRACKS/CORPORATE or TRACKS/KIDS. |
| Era | `80s`, `90s`, `Vintage` | Keywords or Description |
| Instrument | `Piano`, `Guitar` | CatID and Description |

**When is genre required?**

| Sound type | Genre / Subgenre |
|---|---|
| TRACKS | **Required.** The TRACKS category (CatID) must match the genre's column in GENRES.md. |
| STEM | **Required**, same genre as the track. |
| Loops (all music categories) and SAMPLE | **Required** when the loop has a clear style, for example `Hip Hop` / `Boom Bap`. |
| One-shots | Optional. Only when the sound is made for a genre, for example a trap 808. |
| Music FX (risers, impacts …) | Optional. |
| AI GENERATED/MUSICAL | As for TRACKS and loops. |
| Sound effects (official UCS and the rest of AI GENERATED) | Not used. |

**Where the fields are stored:** a field named `Genre` (and `Subgenre`), as user-defined fields
in Soundminer or BaseHead. WAV files also have `IGNR` (Genre) in the INFO chunk, and MP3 has the
ID3 frame `TCON`. If there is only room for one genre field, write `Hip Hop; UK Drill`.

**Examples**

| File | Genre | Subgenre |
|---|---|---|
| `TRKHiphop_Night Shift Full_JLP_LONDONBEATS_142bpm Fsharpmin.wav` | Hip Hop | UK Drill |
| `DRMLoop_Funky Break Loop 01_JLP_SPACEDRUMS_96bpm.wav` | Hip Hop | Boom Bap |
| `SYNTHLead_Saw Lead Riff 03_JLP_NEONPACK_124bpm Fmin.wav` | Trance & Hard Dance | Trance |
| `GITRBanjo_Bluegrass Roll Loop 02_JLP_PORCH_120bpm G.wav` | Folk & Country | Bluegrass |
| `TRKCine_Rise Of The North Full_JLP_NORDICSCORE_100bpm Dmin.wav` | Cinematic | Orchestral; Nordic Folk |
| `BASS808_Long Distorted 808 01_JLP_TRAPKIT_C1.wav` | Hip Hop | Trap |
| `DRMKick_Punchy Acoustic Kick 04_JLP_LIVEKIT.wav` | *(empty)* | *(empty)* |

---

## 8. Rules per category

| Category | FX Name starts with | Must be in the Description | UserData |
|---|---|---|---|
| DRUMS (one-shot) | character + drum: `Tight Snare` | drum machine or kit, room/mic | root note if tuned |
| DRUMS (loop, break, fill) | style + `Loop`/`Break`/`Fill` | bars, time signature, style | `96bpm` |
| PERCUSSION | instrument: `Conga Slap`, `Shaker Loop` | playing technique | `bpm` for loops |
| TUNED PERCUSSION / KEYS | instrument + role: `Rhodes Chords` | model, technique | `bpm` + key, or root note |
| SYNTH | character + role: `Saw Lead Riff` | synth and plugin, development | `bpm` + key, or root note |
| BASS | type + character: `Long Distorted 808` | glide and length | **root note** (one-shot), or `bpm` + key |
| GUITAR / STRINGS / BRASS / WOODWINDS / WORLD | instrument + technique: `Banjo Roll Loop` | instrument, articulation, mic | `bpm` + key |
| VOCALS | character + type: `Airy Female Chop` | lyrics in quotes, language, voice type | `bpm` + key |
| SAMPLE | style + type: `Dusty Soul Loop` | source and origin (rights!) | `bpm` + key |
| FX | type + character: `White Noise Riser` | length, direction | `bpm` if tempo-synced |
| TRACKS | **track title** + version: `Rise Of The North Full` | mood, instrumentation, length (genre in its own field) | `bpm` + key |
| STEM | track title + stem: `Rise Of The North Drums` | which track, what the stem contains | same `bpm` and key as the track |
| AI GENERATED | as for the category the sound would otherwise have | **tool, model and version, and prompt** | as otherwise |

### TRACKS: versions

Use the same version names at the end of FX Name across the whole library:

`Full` · `Instrumental` · `60s` · `30s` · `15s` · `Loop` · `Stinger` · `Alt` · `Underscore`

```
TRKCine_Rise Of The North Full_JLP_NORDICSCORE_100bpm Dmin.wav
TRKCine_Rise Of The North 30s_JLP_NORDICSCORE_100bpm Dmin.wav
STEMDrums_Rise Of The North Drums_JLP_NORDICSCORE_100bpm Dmin.wav
```

### AI GENERATED: transparency

- Always write the **tool, model and version** in the Description, for example "Generated with
  ElevenLabs Sound Effects v2". Add the **prompt** too when you can.
- Put the tool name in Keywords: `ElevenLabs`, `Suno` and so on.
- Check the tool's license terms before the sound is sold or shared, and state the license in the
  library documentation.
- If you edited the sound heavily afterwards, say so: "AI-generated source, edited and layered by hand."

---

## 9. Checklist before publishing

- [ ] The CatID is correct. Run `python tools/build_catalog.py --match "file.wav"` to check.
- [ ] No underscores inside FX Name, and no special characters in the file name.
- [ ] FX Name is at most 25 characters, in Title Case, says what the sound is and has a two-digit number.
- [ ] Loops have `Loop` in FX Name, BPM in UserData, and loop seamlessly.
- [ ] Keys are spelled as in the table (`Fmin`, `Bb`). Pitched one-shots have a root note (`C1`).
- [ ] The Description is in English, most important first, with no marketing.
- [ ] Keywords are 5–20 words, without genre, BPM, key or repetition.
- [ ] Genre and Subgenre are spelled exactly as in GENRES.md. They are required for TRACKS, STEM and loops with a clear style.
- [ ] The TRACKS category (CatID) matches the genre.
- [ ] AI sounds have tool, model and version in the Description.
- [ ] Stems have the same BPM and key as the track.
