# UCSFilesManager – kategorier og nøkkelord

Denne veiledningen forklarer hvordan UCSFilesManager bestemmer hvor en lydfil skal havne,
hvilke kategorier som finnes, hvordan du navngir filer så de sorteres riktig, og hvordan du
endrer kategorier og nøkkelord selv.

Den komplette listen over alle kategorier, underkategorier og nøkkelord står i
[KATALOG.md](KATALOG.md). Den lages automatisk fra kategorilisten.

Hvordan FX Name, Description, Keywords, sjanger, BPM og toneart skal skrives står i
[METADATA-STILGUIDE.md](METADATA-STILGUIDE.md). Den faste sjangerlisten står i [SJANGRE.md](SJANGRE.md).

---

## 1. Kort om UCS

[Universal Category System](https://universalcategorysystem.com) (UCS) er en felles standard
for å navngi og sortere lydeffekter. Hver lyd får en **CatID** som står først i filnavnet:

```
DOORCreak_gammel_låvedør_01.wav
└─CatID─┘
```

CatID-en peker på en **kategori** og en **underkategori**, som også blir mappene filen flyttes til:

```
UCS/DOORS/CREAK/DOORCreak_gammel_låvedør_01.wav
```

Kategorilisten i dette prosjektet består av tre deler:

| Del | Innhold | Antall |
|---|---|---|
| Offisiell UCS | 82 kategorier: AIR, DOORS, WEAPONS … | 753 CatID-er |
| AI GENERATED | Én underkategori per offisiell UCS-kategori, 10 AI-egne underkategorier + MISC | 92 CatID-er |
| Musikkproduksjon | 17 kategorier for instrumenter, loops, stems og ferdige låter | 167 CatID-er |

---

## 2. Slik finner programmet riktig kategori

Programmet gjør to ting, i denne rekkefølgen.

### Steg 1: Filer som allerede har en UCS-CatID

Hvis filnavnet **begynner med** en kjent CatID, blir filen flyttet rett til riktig mappe uten
å endre navnet. `SYNTHPad_warm.wav` går rett til `SYNTH/PAD/`.

Det skilles mellom store og små bokstaver: `SYNTHPad_…` gjenkjennes, `synthpad_…` gjør det ikke.

### Steg 2: Alle andre filer – poeng per ord

1. Filnavnet gjøres om til små bokstaver, og mellomrom blir til `_`.
2. Navnet deles opp i ord på `_`.
3. Hver CatID får **ett poeng for hvert ord** som også står i nøkkelordlisten dens.
4. CatID-en med flest poeng vinner. Står flere likt, viser programmet et valgvindu.

Eksempel: `Synth Lead Saw 01.wav` blir til ordene `synth`, `lead`, `saw` og `01`.

| CatID | Ord som treffer | Poeng |
|---|---|---|
| SYNTHLead | synth, lead, saw | **3** |
| SYNTHPad | synth, saw | 2 |
| VOCLLead | lead | 1 |

`SYNTHLead` vinner, og filen blir hetende `SYNTHLead_Synth Lead Saw 01_….wav`.

Ingen poeng betyr at programmet ikke kan foreslå noe, og da må du velge fra hele listen.

---

## 3. Navngi filer så de havner riktig

- **Skill ordene med `_` eller mellomrom.** `Kick_01` og `Kick 01` gir ordet `kick`.
  `Kick01` er ett ord og treffer ingenting.
- **Bindestrek deler ikke ord.** `hi-hat` er ett ord, og det står derfor også i listen.
- **Skriv både instrument og rolle.** `synth_pad` treffer bedre enn bare `pad`, og
  `vocal_chop` bedre enn bare `chop`.
- **Én loop med ett instrument:** skriv instrumentet og «loop», for eksempel
  `banjo_loop_90.wav`. Den havner da hos BANJO (se 4.3).
- **AI-genererte lyder:** ta med et AI-ord (`ai`, `elevenlabs`, `suno`, `tts` …) sammen med
  hva lyden er, for eksempel `AI_explosion_big.wav` eller `elevenlabs dog bark.wav`.
- **Norske ord fungerer også** for de vanligste instrumentene og sjangrene: `skarptromme`,
  `kassegitar`, `fiolin`, `trekkspill`, `munnspill`, `hardingfele`, `joik`, `filmmusikk` …
- Tall, toneart og tempo (`120`, `Am`, `bpm`) gjør ingen skade. De gir bare ikke poeng.

Sjekk et filnavn før du flytter noe:

```
python tools/build_catalog.py --match "Vocal Chop Am 120.wav"
```

---

## 4. Kategoriene

### 4.1 Offisiell UCS

De 82 offisielle kategoriene og nøkkelordene deres er uendret fra UCS. Prosjektet har bare lagt til
noen ekstra nøkkelord, som `footstep`/`footsteps` i FOOTSTEPS.

### 4.2 AI GENERATED

AI-lyder får egne mapper med samme inndeling som UCS:
`AI GENERATED/EXPLOSIONS` (`AIExpl`), `AI GENERATED/ANIMALS` (`AIAnml`) og så videre.
ARCHIVED er utelatt fordi den er en administrativ mappe og ikke en lydtype. AI-lyder som
ikke passer noe annet sted går i `AI GENERATED/MISC` (`AIMisc`).

#### Lyder som bare finnes med AI

Generativ AI kan lage lyder som ikke har noe motstykke i naturen eller i et opptak. De har
egne underkategorier:

| Underkategori | CatID | Hva | Eksempel på filnavn |
|---|---|---|---|
| MORPH | `AIMorph` | Én lyd som gradvis blir til en annen | `ai_morph_dog_into_car` |
| HYBRID | `AIHybrid` | To kilder smeltet sammen samtidig | `ai_hybrid_lion_engine` |
| TIMBRE TRANSFER | `AITimbre` | En framføring gjengitt med en annen klang | `timbre_transfer_voice_to_violin` |
| IMAGINARY INSTRUMENT | `AIInstr` | Instrumenter som ikke finnes | `ai_imaginary_instrument` |
| IMAGINARY WORLD | `AIWorld` | Lydbilder fra steder som ikke finnes | `ai_alien_planet_ambience` |
| IMPOSSIBLE PHYSICS | `AIPhys` | Lyder som bryter fysikken | `ai_impossible_glass_bend` |
| SURREAL | `AISurr` | Drømmeaktig, uhyggelig, liminalt | `ai_surreal_dream` |
| GIBBERISH | `AIGibb` | Tale uten ekte språk | `ai_gibberish_speech` |
| ARTIFACT | `AIArtf` | Lyden av modellen selv: hallusinasjoner, metallisk «smøring» | `ai_artifact_garbled` |
| LATENT SPACE | `AILatent` | Tilfeldige generasjoner uten prompt, latent-vandringer | `ai_latent_walk` |

#### Nøkkelordene

Nøkkelordene i hver AI-underkategori er satt sammen av tre deler:

1. **AI-ord** som står i alle AI-underkategoriene: `ai, aigen, aigenerated, ai-generated, genai,
   elevenlabs, stableaudio, audiogen, audiocraft, audioldm, texttoaudio, text2audio, ki,
   kigenerert`. «generated» og «generative» er bevisst utelatt, fordi generativ musikk og
   prosedyregenererte lyder ikke trenger å være AI.
2. **Kategoriord**, for eksempel `explosion` og `explosions`.
3. **Ordene fra de offisielle underkategoriene**, for eksempel `dog`, `horse` og `rifle`.
   Tre slags ord er utelatt:
   - ord som går igjen i tre eller flere kategorier, som `misc`, `impact` og `handle`
   - ord som også er musikk-nøkkelord, som `bass` fra DESIGNED/BASS DIVE og `track` fra
     SPORTS/TRACK & FIELD. Ellers ville «ai_bass» havnet i AI GENERATED/DESIGNED.
   - ord som tilhører de AI-egne underkategoriene, som `morph` fra DESIGNED/MORPH

I tillegg har to AI-underkategorier egne verktøynavn:

| Underkategori | Verktøynavn |
|---|---|
| AI GENERATED/MUSICAL | suno, udio, musicgen, mubert, aiva, soundraw, boomy, riffusion, lyria |
| AI GENERATED/VOICES | tts, texttospeech, voiceclone, respeecher, playht, narrator |

En vanlig fil som `Wood_Door_Creak.wav` får ikke et AI-alternativ, fordi den mangler AI-ordet.

**AI-musikk og -instrumenter:** `ai_drum_loop.wav` havner i DRUMS/LOOP og ikke i AI GENERATED,
fordi «drum» og «loop» gir to poeng mens AI-ordet bare gir ett. Programmet kan ikke kreve «AI-ord
*og* trommeord». Det kan bare telle treff. Vet du at en fil er AI-generert, gjør du ett av to:
- gi filen CatID-en direkte først i navnet (`AIMusc_drum_loop.wav`), så flyttes den uten å
  spørre
- ta med verktøynavnet og et musikkord (`suno_ai_song`), og velg AI GENERATED/MUSICAL i valgvinduet

### 4.3 Musikkproduksjon

| Kategori | CatShort | Underkategorier |
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

#### Reglene bak inndelingen

**1. Først instrumentfamilie, så rolle.** Spillestil som chords, riff og distorted er ikke en egen
kategori, med unntak av det som er vanlig i sample-pakker: synth lead/pad/pluck, vocal chop og drum loop.

**2. Familieord + rolleord.** Alle underkategorier i en familie har familiens ord
(alle SYNTH-oppføringer har `synth, synths, analog, moog, juno …`), og hver underkategori har
i tillegg sine egne ord. Det er det som gjør at ord som peker hver sin vei likevel havner riktig:

| Filnavn | Havner i | Fordi |
|---|---|---|
| `synth_bass` | BASS/SYNTH | «synth» og «bass» står begge der |
| `brass_stab` | BRASS/ENSEMBLE | «brass» og «stab» |
| `vocal_chop` | VOCALS/CHOP | «vocal» og «chop» |
| `drum_stem` | STEM/DRUMS | «drum» og «stem» |
| `orchestral_track` | TRACKS/CINEMATIC | «orchestral» og «track» |

**3. Loops havner hos instrumentet.** Underkategorien sier *hva* som spiller, ikke om det er en
loop eller en enkeltlyd. Ordet «loop» blir stående i filnavnet, så det går fortsatt an å søke på det.

| Filnavn | Havner i |
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

LOOP-underkategorier finnes bare der en loop blander flere instrumenter: DRUMS (LOOP og
TOP LOOP), PERCUSSION og SAMPLE. Hele låter går i TRACKS.

Unntak, slik at regelen fungerer i praksis:

- **PERCUSSION/LOOP og MISC** er de eneste perkusjons-underkategoriene med familieordene
  (`perc, percussion …`). Hvis alle hadde dem, ville «perc_loop» endt uavgjort med HAND DRUM,
  SHAKER og resten.
- **DRUMS/TOP LOOP** har «loop», men ikke trommeordene. Da går «drum_loop» til DRUMS/LOOP.
- **TUNED PERCUSSION/STEEL DRUM** har «drum» (steel drum), men ikke «loop». Ellers ville
  den tatt trommeloops.

**4. Ingen overlapp med offisiell UCS der det kan unngås.** Musikkvokal er `VOCALS`/`VOCL`, mens
`VOICES`/`VOX` er uendret fra UCS. Foley og feltopptak hører hjemme i offisielle `FOLEY` og `AMBIENCE`.

Den offisielle `MUSICAL` dekker noen av de samme instrumentene, som `MUSCWind`, `MUSCStr` og `MUSCKeyd`.
Et filnavn med bare ett instrumentord, som `clarinet.wav`, får derfor to forslag: WOODWINDS/CLARINET
og MUSICAL/WOODWIND. Begge er riktige, og du velger det som passer biblioteket ditt.

**5. TRACKS sorteres etter sjanger.** Hver sjanger i [SJANGRE.md](SJANGRE.md) peker på én TRACKS-kategori,
og sjangernavnene står som nøkkelord der («amapiano_track» havner i TRACKS/WORLD). Navn som også er
instrument- eller lydeffektord (breakbeat, folk, industrial) er ikke tatt med. STINGER (seier, game over, level complete) og JINGLE
(jingler, lydlogoer, identer) er unntak, fordi korte stikk kan være i alle sjangre.

**6. Alle familier har MISC** for det som ikke passer andre steder.

---

## 5. Endre nøkkelord og kategorier

Kategorilisten ligger i `catalog/` og kan åpnes i Numbers, Excel eller en teksteditor:

| Fil | Innhold |
|---|---|
| `catalog/ucs_official.csv` | Offisiell UCS med alle oversettelser |
| `catalog/custom_categories.csv` | AI GENERATED og musikkategoriene |
| `catalog/match_tests.csv` | Testfilnavn og hvor de skal havne |
| `catalog/genres.csv` | Sjangerlisten for metadatafeltene Genre og Subgenre, med TRACKS-kategori og typisk BPM |

`data.txt`, `keywords/*.txt`, `UCS(folders).zip`, `catalog/_categorylist.xlsx` og
`docs/KATALOG.md` **lages fra CSV-filene**. Endrer du `keywords/*.txt` direkte, blir det
overskrevet neste gang listen bygges.

### Legge til et nøkkelord

1. Åpne `catalog/custom_categories.csv` (eller `ucs_official.csv`).
2. Finn raden og legg ordet til i kolonnen **Synonyms - Comma Separated**, skilt med komma.
3. Kjør `python tools/build_catalog.py --test` og så `python tools/build_catalog.py`.

### Regler for nøkkelord

- **Bare enkeltord.** «french horn» kan aldri treffe. Skriv `frenchhorn` og `horn`.
- **Bare små bokstaver.** Programmet gjør filnavnet om til små bokstaver før det sammenligner.
- **Flertall er ikke automatisk.** Skriv både `kick` og `kicks`.
- **Æ, ø, å og aksenter går fint.** Byggeskriptet legger automatisk til skrivemåten Mac kan
  bruke for slike tegn i filnavn, der «å» lagres som «a» pluss en ring. Legg gjerne til en ASCII-variant
  også (`seljefloyte` ved siden av `seljefløyte`) for folk som skriver uten æøå.
- **Ord som er fjernet med vilje.** I logikkgjennomgangen ble disse ordene tatt ut fordi de dro
  urelaterte filer inn i én underkategori:
  - `saw`: en håndsag havnet i SYNTH
  - `gate`: kolliderte med DOORS/GATE
  - `vintage`: «vintage_synth» havnet i SAMPLE/VINYL
  - `legato`/`staccato`: blåsere havnet i STRINGS
  - `swell`: strykere havnet i BRASS
  - `bars`: «8 bars» havnet i VOCALS/RAP
  - `dark`, `calm`, `action`: stemningsord som dro filer inn i TRACKS
  - `game`, `success`, `fail`: UI-lyder havnet i TRACKS/STINGER
  - `acoustic`, `electronic`: beskrivelser, ikke trommeord
  - `slam`, `flow`, `scratching`, `digital`, `crunch`, `drill`, `grime`, `swing`: vanlige
    lydeffektord (dørsmell, vannføring, drill) som dro lydeffekter inn i musikk-kategoriene
- **Ikke legg vanlige ord på én enkelt underkategori.** Ord som `hit`, `loop` og `melody` står
  i mange filnavn. Står et slikt ord bare på én underkategori, trekker den til seg filer som
  egentlig hører hjemme andre steder. Kjør testene etter hver endring.

### Legge til en underkategori

Legg til en rad med Category, SubCategory, CatID, CatShort, Explanations og nøkkelord.
Byggeskriptet avviser raden hvis:

- CatID-en allerede finnes, eller kategori/underkategori-paret allerede er brukt
- et navn inneholder komma (det ødelegger `data.txt`)
- CatID-en inneholder mellomrom, `_` eller `-`
- CatID-en ikke begynner med CatShort
- CatID-en er starten på en annen CatID, eller omvendt. Da ville programmet flyttet filer
  som allerede har UCS-navn til feil mappe.
- raden mangler nøkkelord, har nøkkelord med mellomrom eller har store bokstaver
- Category eller SubCategory ikke er skrevet med store bokstaver

### Kommandoer

```
python tools/build_catalog.py            # sjekk og bygg alt
python tools/build_catalog.py --check    # bare sjekk
python tools/build_catalog.py --test     # kjør testene i catalog/match_tests.csv
python tools/build_catalog.py --match "fil.wav" "fil2.wav"   # vis hva programmet vil foreslå
python tools/build_docs.py               # lag docs/KATALOG.md og docs/SJANGRE.md
python tools/build_docs.py --pdf         # lag også docs/UCS-katalog.pdf (krever markdown og Chromium/Chrome)
```

Byggeskriptet bruker bare Python sitt standardbibliotek. `openpyxl` trengs bare for
regnearket `_categorylist.xlsx`, og `markdown` bare for PDF-en.

### Testene

`catalog/match_tests.csv` har én linje per filnavn: filen, CatID-en den skal få, og hvor
mange valg valgvinduet høyst kan vise. Legg til en linje hver gang du finner et filnavn som
havner feil, rett nøkkelordene og kjør `--test` til alt består.

---

## 6. Kjente begrensninger

Disse ligger i selve programmet (`UCSFilesManager.exe`). Kildekoden (`V37.py`) er ikke med i
repoet, så de kan ikke rettes herfra.

- **Bare `.wav`, `.mp3`, `.flac` og `.aac` blir funnet.** `.aif`/`.aiff` og `.ogg` blir
  hoppet over, enda `.aif` er vanlig i sample-pakker.
- **Bare `_` og mellomrom skiller ord.** `Kick01`, `kick-01` og `kick.01` blir ikke til `kick`.
- **Nøkkelord med mellomrom kan aldri treffe.** Fem offisielle UCS-nøkkelord har dette
  problemet, og byggeskriptet viser dem som advarsler.
- **Offisielle ROBOTS og SCIFI har «ai» som nøkkelord.** `ai_robot_voice.wav` kan derfor få
  forslag fra både AI GENERATED og offisielle ROBOTS.
- **Store og små bokstaver teller for filer med UCS-navn.** `drmkick_01.wav` gjenkjennes ikke
  som `DRMKick`.

---

## 7. Fra første utkast (`_categorylist.numbers`)

Har du allerede gitt filer navn med CatID-er fra det første regnearket (`DRMKi`, `WOWIFlu` …),
står det i `catalog/README.md` hvilke nye CatID-er de tilsvarer.
