# UCS Musikk – metadata-stilguide

Slik skriver du filnavn, FX Name, Description, Keywords, sjanger og musikalsk informasjon (BPM og toneart)
for lydene i musikk-kategoriene: DRUMS, SYNTH, VOCALS, TRACKS, STEM og de andre. Det samme gjelder
for AI GENERATED.

> **Grunnlag.** Guiden følger UCS-spesifikasjonen for filnavn og felt, og vanlig praksis i
> kommersielle lyd- og sample-bibliotek. Stilguiden til A Sound Effect
> (asoundeffect.com/metadata-style-guide) var ikke tilgjengelig da guiden ble skrevet, så den er
> **ikke kontrollert mot den**. Avvik derfra bør rettes her.

---

## 1. Feltene som beskriver en lyd

| Hvor | Felt | Hva det er til | Eksempel |
|---|---|---|---|
| Filnavn | **CatID** | Sorterer filen i riktig mappe | `SYNTHLead` |
| Filnavn | **FX Name** | Kort tittel som leses i en fil-liste | `Saw Lead Riff 03` |
| Metadata | **Description** | Hele beskrivelsen, det man søker og leser i | `Bright detuned saw lead playing a syncopated riff…` |
| Metadata | **Keywords** | Ord som ikke står i Description, men som noen vil søke etter | `Supersaw, Festival, Anthem` |
| Metadata | **Genre** | Hovedsjanger fra den faste listen | `Trance & Hard Dance` |
| Metadata | **Subgenre** | Undersjanger fra den faste listen | `Trance` |

For musikk kommer **BPM**, **Key** (toneart), **Bars** og **Time Signature** i tillegg.

**Språk:** skriv metadata på **engelsk**. Søkeverktøyene, UCS-katalogen og kundene bruker engelsk.
Norske ord kan legges i Keywords i tillegg, men aldri i stedet for de engelske.

---

## 2. Filnavnet

UCS-filnavnet har faste felt, adskilt med understrek:

```
CatID_FX Name_CreatorID_SourceID_UserData.wav
```

| Felt | Regel | Eksempel |
|---|---|---|
| CatID | Nøyaktig som i katalogen, med samme store og små bokstaver | `BASS808` |
| FX Name | Kort tittel. Se kapittel 3. | `Long Distorted 808 01` |
| CreatorID | Den som har laget lyden: initialer eller kort navn | `JLP` |
| SourceID | Biblioteket eller prosjektet, kort og med store bokstaver | `TRAPKIT` |
| UserData | Musikalsk informasjon: BPM, toneart eller grunntone | `140bpm Fmin` |

**Regler for hele filnavnet**

- **Understrek skiller felt og skal ikke brukes inne i et felt.** Bruk mellomrom inne i FX Name.
  - Riktig: `Saw Lead Riff 03`
  - Feil: `Saw_Lead_Riff_03`, fordi da tror alle UCS-verktøy at «Lead» er CreatorID.
- **Bare bokstavene A–Z, tall, mellomrom og bindestrek.** Ingen æ, ø, å, aksenter, `/`, `#`,
  `&`, `( )`, `?` eller `*`.
  - Grunnen er at filnavn med spesialtegn kan endre seg mellom Mac og Windows, eller bli
    ødelagt i zip-filer og skytjenester.
  - Unntak: `#` i tonearter. Skriv `Csharp` eller `Db` i filnavnet, og `C#` i metadata.
- **Nummerering:** to sifre på slutten av FX Name, med mellomrom foran: `01`, `02` … `99`.
  Nummeret skiller varianter av samme lyd. Det er ikke en versjonsnummerering.
- **Ingen dato, «final», «v2», «new» eller «copy»** i filnavn som skal publiseres.

**Eksempler**

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

### I UCSFilesManager

Programmet setter CatID foran og bruker det opprinnelige filnavnet som FX Name. Gjør derfor dette:

1. **Rydd filnavnet før du kjører programmet**, slik at det allerede er et godt FX Name
   (kapittel 3). Programmet fjerner `(` og `)`, men retter ingenting annet.
2. I **UCS Custom Format** skriver du resten av navnet, for eksempel `$filename_JLP_NEONPACK`.
3. BPM og toneart legger du til selv, enten i det opprinnelige filnavnet bakerst eller etterpå.

Programmet skriver **bare filnavnet**. Description, Keywords, BPM og Key må skrives inn i
filens metadata (BWF/iXML) med et eget verktøy, for eksempel Soundminer, BaseHead eller Reaper.

---

## 3. FX Name

FX Name er tittelen man ser i en fil-liste. Den skal kunne leses på ett sekund.

**Regler**

- **Høyst 25 tegn**, som UCS anbefaler. Nummeret teller med.
- **Stor forbokstav i hvert ord** (Title Case): `Warm Rhodes Chords 02`
- **Rekkefølge:** `[Karakter] [Kilde/instrument] [Rolle/handling] [Loop] [Nummer]`
  - `Tight Snare 03`
  - `Dusty Rhodes Chords Loop 02`
  - `Airy Female Vocal Chop 07`
- **Skriv `Loop` i FX Name for alle loops.** Loops ligger sammen med enkeltlydene i
  instrumentmappen (BANJO, PIANO …), så det er ordet «Loop» som skiller dem.
- **Ikke skriv BPM, toneart eller taktart i FX Name.** De hører hjemme i UserData og metadata.
- **Ikke gjenta CatID-en hvis du trenger plassen.** I `DRMKick` er «Kick» allerede sagt.
  Skriv det likevel hvis det er plass, for navnet skal være lesbart uten CatID-en.
- **Ingen interne koder eller forkortelser** som bare du forstår. `Rhodes` er greit, `RHD_MK1` er det ikke.

| Dårlig | Bra | Hvorfor |
|---|---|---|
| `kick_final_v2` | `Punchy Kick 02` | ingen versjon, Title Case, mellomrom |
| `Lead 124bpm Fmin` | `Saw Lead Riff 03` | BPM og toneart hører hjemme i UserData |
| `Synth Thing` | `Wobbly Pluck Arp 01` | sier hva det er |
| `Beautiful Emotional Cinematic Piano Chords` | `Soft Piano Chords 04` | under 25 tegn, stemning hører hjemme i Description |

---

## 4. Description

Description er feltet som blir søkt i og lest, og det viktigste feltet etter CatID.

**Regler**

- **En til tre setninger på engelsk, med vanlige setningsstore bokstaver og punktum til slutt.**
- **Det viktigste først.** Mange verktøy viser bare de første 60–80 tegnene.
- **Fast rekkefølge:**
  1. **Hva:** kilde eller instrument og rolle. «Warm Rhodes electric piano playing a slow chord progression.»
  2. **Hvordan:** karakter, spilleteknikk og utvikling. «Soft attack, tremolo, swells in the last bar.»
  3. **Musikalsk:** BPM, toneart, takter og taktart. «4 bars, 90 BPM, D minor, 4/4.»
  4. **Kilde/teknikk**, hvis det er nyttig: instrumentmodell, mikrofon, forsterker og
     prosessering. «Fender Rhodes Mk I through a Fender Twin, close mic.»
- **Beskriv det man hører, ikke det man føler.** «Bright, detuned, fast attack» er bra.
  «Amazing, epic, insane» er ikke.
- **Ingen markedsføring**, ingen «perfect for …» og ingen emojis.
- **Tekst som synges eller sies** skrives i anførselstegn, og språket nevnes:
  `Female vocal phrase singing "hold me closer" in English.`
- **Gjenta gjerne ordene fra FX Name.** Description skal kunne leses alene.

**Eksempler**

| Fil | Description |
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

Keywords er for ord som noen vil søke etter, men som **ikke** står i FX Name eller Description.

**Regler**

- **Kommaseparert, i Title Case som i UCS:** `Supersaw, Trance, Festival, Anthem`
- **5–20 ord.** Flere ord gir dårligere søketreff, ikke bedre.
- **Ta med** synonymer (`Uplifter` for Riser), instrumentnavn og modeller (`Juno`, `Rhodes`, `808`),
  stemning (`Dark`, `Uplifting`), spilleteknikk og artikulasjon (`Pizzicato`, `Palm Mute`)
  og vanlige skrivemåter (`Hi-Hat, Hihat, Hat`).
- **Ikke ta med** sjanger, BPM, toneart, CreatorID, SourceID eller filformat. De har egne felt.
- **Ikke gjenta ord** fra FX Name og Description. De blir søkt i uansett.
- **Ikke fyll på med alt mulig** («keyword stuffing»). Hvert ord skal stemme for akkurat denne lyden.

**Eksempel for synth-leaden**

```
Supersaw, Festival, Anthem, Hook, Melody, Detuned Saw, Euphoric
```

> Ikke bland dette feltet sammen med `keywords/*.txt` i UCSFilesManager. De filene brukes av
> programmet til å *finne* CatID og har egne regler: enkeltord og små bokstaver. Se
> BRUKERVEILEDNING.md. Feltet Keywords i metadata kan ha flere ord sammen, som `Palm Mute`.

---

## 6. Musikalsk informasjon

### BPM

- Heltall: `124`. Bruk desimaler bare når tempoet faktisk er det: `92.5`.
- I filnavnet (UserData) skrives `124bpm` med små bokstaver og uten mellomrom.
  I metadata står bare tallet i BPM-feltet, og `124 BPM` i Description.
- **Loops må loope sømløst og være et helt antall takter** i oppgitt BPM.
- Enkeltlyder (one-shots) får ikke BPM.

### Toneart (Key)

Én fast skrivemåte for alle 24 tonearter:

| Dur (major) | Moll (minor) |
|---|---|
| C, G, D, A, E, B, F#, Db, Ab, Eb, Bb, F | Amin, Emin, Bmin, F#min, C#min, G#min, Ebmin, Bbmin, Fmin, Cmin, Gmin, Dmin |

- **Dur skrives som bare tonen:** `G`. **Moll får `min`:** `Amin`. Ikke `Am`, `A minor`, `a` eller `Amoll`.
- **Bruk samme navn for samme tone**, som i tabellen: `F#`, `Db`, `Ab`, `Eb` og `Bb`.
  Skriv aldri `A#` når tabellen sier `Bb`.
- I **filnavn** skrives `#` som `sharp`: `F#min` blir `Fsharpmin`. I metadata skrives `F#min`.
- I Description skrives tonearten helt ut: `F sharp minor`, `D major`.
- **Atonalt materiale** (støy, perkusjon, FX) får ikke toneart.

### Grunntone for enkeltlyder

Bass, 808, synth- og instrumentnoter som én enkelt tone får **grunntone med oktav**:
`C1`, `F#2`, `A3`.

- **Bruk vitenskapelig tonehøyde: `C4` er midt-C (261,6 Hz) og `A4` er 440 Hz.** Merk at
  Ableton og noen andre DAW-er kaller midt-C for `C3`, så det må stå i bibliotekets
  dokumentasjon hvilken konvensjon som er brukt.
- En stemt kick eller tom kan få grunntone. En kick som ikke er stemt får ikke det.

### Takter og taktart

- I Description: `4 bars, 4/4`. Taktart skrives aldri i filnavnet, fordi `/` ikke er lov i filnavn.
- Oppgi taktart bare når den ikke er 4/4, eller alltid. Velg én regel for hele biblioteket.

---

## 7. Sjanger (Genre og Subgenre)

Sjanger har **to egne metadatafelt**: `Genre` og `Subgenre`. Begge velges fra den faste listen i
[SJANGRE.md](SJANGRE.md), som lages fra `catalog/genres.csv`. Listen har 17 hovedsjangre og rundt
130 undersjangre, med typisk BPM og hvilken TRACKS-kategori de hører til.

| Hovedsjangre |
|---|
| Hip Hop · R&B & Soul · Pop · House · Techno · Trance & Hard Dance · Dance & EDM · Bass Music · Electronic · Rock · Jazz & Blues · Folk & Country · Latin & Caribbean · Afro · Global · Cinematic · Classical |

**Regler**

- **Genre: nøyaktig én hovedsjanger** fra listen.
- **Subgenre: ingen, én eller to undersjangre** fra listen, skilt med semikolon:
  `UK Drill` eller `UK Drill; Grime`.
  - Den første må høre til hovedsjangeren.
  - Den andre kan komme fra en annen hovedsjanger når lyden er en blanding.
- **La Subgenre stå tom** når lyden bare er «generell» i hovedsjangeren, for eksempel vanlig pop eller rock.
  Listen har derfor ingen undersjanger som heter «Pop» eller «Rock».
- **Skriv navnene nøyaktig som i listen:** samme store og små bokstaver, `&` og bindestrek.
  `Drum & Bass`, ikke `DnB` eller `Drum and Bass`. `Lo-Fi Hip Hop`, ikke `lofi`.
- **Ikke finn på nye sjangre i feltet.** Mangler en sjanger, legg den til i `catalog/genres.csv`
  (med hovedsjanger, TRACKS-kategori, typisk BPM og en kort beskrivelse) og kjør
  `python tools/build_catalog.py --check`.
- **Sjanger hører ikke hjemme i filnavnet eller i Keywords.** Den har sitt eget felt. Skriv den gjerne
  naturlig i Description når den beskriver lyden: «UK drill beat with sliding 808s».

**Dette er ikke sjangre**, og skal i Keywords eller Description i stedet:

| Type | Eksempler | Hvor |
|---|---|---|
| Framføring | `Live Instruments`, `Acoustic`, `Unplugged` | Keywords |
| Stemning | `Dark`, `Happy`, `Uplifting`, `Melancholic` | Keywords |
| Bruk | `Corporate`, `Kids`, `Vlog`, `Podcast` | Keywords. For hele låter kan CatID være TRACKS/CORPORATE eller TRACKS/KIDS. |
| Epoke | `80s`, `90s`, `Vintage` | Keywords eller Description |
| Instrument | `Piano`, `Guitar` | CatID og Description |

**Når skal sjanger fylles ut?**

| Lydtype | Genre / Subgenre |
|---|---|
| TRACKS | **Påkrevd.** TRACKS-kategorien (CatID) skal stemme med sjangerens kolonne i SJANGRE.md. |
| STEM | **Påkrevd**, med samme sjanger som låten. |
| Loops (alle musikk-kategorier) og SAMPLE | **Påkrevd** når loopen har en tydelig stil, for eksempel `Hip Hop` / `Boom Bap`. |
| Enkeltlyder (one-shots) | Valgfritt. Bare når lyden er laget for en sjanger, for eksempel et trap-808. |
| FX for musikk (risere, impacts …) | Valgfritt. |
| AI GENERATED/MUSICAL | Som for TRACKS og loops. |
| Lydeffekter (offisiell UCS og resten av AI GENERATED) | Brukes ikke. |

**Hvor feltene lagres:** et eget felt som heter `Genre` (og `Subgenre`), som brukerdefinerte felt i
Soundminer eller BaseHead. I WAV-filer finnes også `IGNR` (Genre) i INFO-blokken, og i MP3 ID3-feltet
`TCON`. Er det bare plass til ett sjangerfelt, skrives `Hip Hop; UK Drill`.

**Eksempler**

| Fil | Genre | Subgenre |
|---|---|---|
| `TRKHiphop_Night Shift Full_JLP_LONDONBEATS_142bpm Fsharpmin.wav` | Hip Hop | UK Drill |
| `DRMLoop_Funky Break Loop 01_JLP_SPACEDRUMS_96bpm.wav` | Hip Hop | Boom Bap |
| `SYNTHLead_Saw Lead Riff 03_JLP_NEONPACK_124bpm Fmin.wav` | Trance & Hard Dance | Trance |
| `GITRBanjo_Bluegrass Roll Loop 02_JLP_PORCH_120bpm G.wav` | Folk & Country | Bluegrass |
| `TRKCine_Rise Of The North Full_JLP_NORDICSCORE_100bpm Dmin.wav` | Cinematic | Orchestral; Nordic Folk |
| `BASS808_Long Distorted 808 01_JLP_TRAPKIT_C1.wav` | Hip Hop | Trap |
| `DRMKick_Punchy Acoustic Kick 04_JLP_LIVEKIT.wav` | *(tom)* | *(tom)* |

---

## 8. Regler per kategori

| Kategori | FX Name begynner med | Må stå i Description | UserData |
|---|---|---|---|
| DRUMS (enkeltlyd) | karakter + tromme: `Tight Snare` | trommemaskin eller kit, rom/mik | grunntone hvis stemt |
| DRUMS (loop, break, fill) | stil + `Loop`/`Break`/`Fill` | takter, taktart, stil | `96bpm` |
| PERCUSSION | instrument: `Conga Slap`, `Shaker Loop` | spilleteknikk | `bpm` for loops |
| TUNED PERCUSSION / KEYS | instrument + rolle: `Rhodes Chords` | modell, teknikk | `bpm` + toneart, eller grunntone |
| SYNTH | karakter + rolle: `Saw Lead Riff` | synth og plugin, utvikling | `bpm` + toneart, eller grunntone |
| BASS | type + karakter: `Long Distorted 808` | glide og lengde | **grunntone** (enkeltlyd), eller `bpm` + toneart |
| GUITAR / STRINGS / BRASS / WOODWINDS / WORLD | instrument + teknikk: `Banjo Roll Loop` | instrument, artikulasjon, mik | `bpm` + toneart |
| VOCALS | karakter + type: `Airy Female Chop` | teksten i anførselstegn, språk, stemmetype | `bpm` + toneart |
| SAMPLE | stil + type: `Dusty Soul Loop` | kilde og opphav (rettigheter!) | `bpm` + toneart |
| FX | type + karakter: `White Noise Riser` | lengde, retning | `bpm` hvis den er synket til tempo |
| TRACKS | **låttittel** + versjon: `Rise Of The North Full` | stemning, instrumentering, lengde (sjanger i eget felt) | `bpm` + toneart |
| STEM | låttittel + stem: `Rise Of The North Drums` | hvilken låt, hva stemmen inneholder | samme `bpm` og toneart som låten |
| AI GENERATED | som for kategorien lyden ellers ville hatt | **verktøy, modell og versjon, og prompt** | som ellers |

### TRACKS: versjoner

Bruk de samme versjonsnavnene bakerst i FX Name i hele biblioteket:

`Full` · `Instrumental` · `60s` · `30s` · `15s` · `Loop` · `Stinger` · `Alt` · `Underscore`

```
TRKCine_Rise Of The North Full_JLP_NORDICSCORE_100bpm Dmin.wav
TRKCine_Rise Of The North 30s_JLP_NORDICSCORE_100bpm Dmin.wav
STEMDrums_Rise Of The North Drums_JLP_NORDICSCORE_100bpm Dmin.wav
```

### AI GENERATED: åpenhet

- Skriv alltid **verktøy, modell og versjon** i Description, for eksempel «Generated with ElevenLabs Sound
  Effects v2». Skriv gjerne **prompten** også.
- Legg verktøynavnet i Keywords: `ElevenLabs`, `Suno` og så videre.
- Sjekk verktøyets lisensvilkår før lyden selges eller deles, og skriv lisensen i bibliotekets dokumentasjon.
- Har du redigert lyden mye etterpå, skriv det: «AI-generated source, edited and layered by hand.»

---

## 9. Sjekkliste før publisering

- [ ] CatID er riktig. Kjør gjerne `python tools/build_catalog.py --match "fil.wav"`.
- [ ] Ingen understrek inne i FX Name, og ingen spesialtegn i filnavnet.
- [ ] FX Name er høyst 25 tegn, i Title Case, sier hva lyden er og har to-sifret nummer.
- [ ] Loops har `Loop` i FX Name, BPM i UserData og looper sømløst.
- [ ] Toneart er skrevet som i tabellen (`Fmin`, `Bb`). Enkeltlyder med tonehøyde har grunntone (`C1`).
- [ ] Description er på engelsk, med det viktigste først, uten markedsføring.
- [ ] Keywords er 5–20 ord, uten sjanger, BPM, toneart og gjentakelser.
- [ ] Genre og Subgenre er skrevet nøyaktig som i SJANGRE.md. De er påkrevd for TRACKS, STEM og loops med tydelig stil.
- [ ] TRACKS-kategorien (CatID) stemmer med sjangeren.
- [ ] AI-lyder har verktøy, modell og versjon i Description.
- [ ] Stems har samme BPM og toneart som låten.
