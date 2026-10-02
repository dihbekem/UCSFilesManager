"""Suggest UCS metadata for every audio file in a folder (for example a sample-pack library) and
write it to a spreadsheet for review: Path, CatID, FX Name, suggested file name, Description,
Genre, Subgenre, BPM, Key, Keywords, and how sure the suggestion is.

    python tools/suggest_metadata.py "/Volumes/Drive/Sample Packs" -o sample-packs.xlsx --creator JLP
    python tools/suggest_metadata.py file-list.txt --root "/Volumes/Drive/Sample Packs" -o out.xlsx

The input is a folder, or a text file with one path per line (for example the output of
`find "/Volumes/Drive/Sample Packs" -type f > file-list.txt`). Nothing is renamed or moved.

The suggestions follow docs/METADATA-STYLE-GUIDE.md. They are drafts made from file and folder
names only (the audio is not analysed), so check every row, above all those marked REVIEW.
Without openpyxl the output is written as CSV instead.
"""
import argparse
import collections
import csv
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_catalog  # noqa: E402

AUDIO = {'.wav', '.aif', '.aiff', '.mp3', '.flac', '.ogg', '.m4a', '.aac'}
AI_MARKERS = {'ai', 'aigen', 'aigenerated', 'ai-generated', 'genai', 'elevenlabs', 'stableaudio', 'audiogen',
              'audiocraft', 'audioldm', 'texttoaudio', 'text2audio', 'suno', 'udio', 'musicgen', 'tts'}
# Folder and file words that say nothing about the sound.
NOISE = {'wav', 'aif', 'aiff', 'mp3', 'flac', 'one', 'shot', 'shots', 'oneshot', 'oneshots', 'one-shot', 'one-shots',
         'sample', 'samples', 'pack', 'kit', 'kits', 'sounds', 'sound', 'audio', 'files', 'file', 'final', 'new',
         'copy', 'edit', 'bounce', 'master', 'stereo', 'mono', 'v1', 'v2', 'v3', 'the', 'and', 'of', 'a',
         'bpm', 'key', 'wet', 'dry', 'demo', 'preview', 'vol', 'volume', 'bonus', 'free', 'misc', 'various',
         'preset', 'presets', 'multi', 'multis', 'session', 'sessions', 'tools', 'tool', 'expansion', 'edition',
         'collection', 'bundle', 'series', 'part', 'ii', 'iii', 'iv', 'vi', 'vii', 'viii', 'ix', 'xi', 'xii',
         'wavs', 'apple', 'ableton', 'kontakt', 'logic', 'maschine', 'rack', 'racks', 'patch', 'patches', 'midi',
         'imported', 'processed', 'freeze', 'bounced', 'render', 'renders', 'export', 'exports', 'bit', 'khz',
         'label', 'labels', 'records', 'recordings', 'production', 'productions', 'producer', 'producers',
         'suite', 'packs', 'library', 'folder', 'untitled', 'audio', 'version', 'versions', 'original', 'alt',
         'take', 'takes', 'main', 'extra', 'extras', 'vst', 'plugin', 'instrument', 'instruments', 'mixed',
         'essentials', 'essential', 'ultimate', 'complete', 'deluxe', 'pro', 'premium', 'mega', 'super',
         'signature', 'launch', 'certified', 'official', 'exclusive', 'limited', 'special', 'vault',
         'single', 'singles', 'elements', 'element', 'gain', 'norm', 'normalized', 'trim', 'trimmed', 'fade', 'faded', 'rendered', 'misc'}
# words that may help pick a CatID but say nothing as a keyword
KEYWORD_NOISE = {'sci', 'fi', 'live', 'real', 'project', 'projects', 'studio', 'template', 'templates', 'thing', 'things',
                 'starter', 'starters', 'inspired', 'style', 'styles', 'type', 'types', 'sampled', 'recorded',
                 'variation', 'variations', 'var', 'off', 'on', 'mix', 'mixes', 'layer', 'layers', 'layered',
                 'stage', 'part', 'parts', 'section', 'sections', 'element', 'elements', 'only', 'killer', 'next',
                 'tails', 'tail', 'builder', 'enhancers', 'design', 'designs', 'virtual', 'stack', 'stacks',
                 'textures', 'machines', 'builds', 'tops', 'top', 'hits', 'hit', 'loops', 'loop', 'shots'}
# describing words used in sample-pack names that the catalog vocabulary doesn't have
DESCRIPTORS = {'warm', 'punchy', 'bright', 'crispy', 'crisp', 'thin', 'wide', 'dirty', 'saturated', 'glassy',
               'smooth', 'harsh', 'mellow', 'huge', 'filtered', 'stuttered', 'emotional', 'sad', 'groovy',
               'bouncy', 'swung', 'subby', 'wobbly', 'plucky', 'gritty', 'dusty', 'airy', 'lush', 'dreamy',
               'snappy', 'boomy', 'fat', 'tight', 'dark', 'soft', 'hard', 'deep', 'heavy', 'clean', 'distorted',
               'vintage', 'analog', 'analogue', 'organic', 'metallic', 'noisy', 'reversed', 'chopped', 'glitchy',
               'granular', 'evolving', 'rhythmic', 'melodic', 'atmospheric', 'cinematic', 'uplifting', 'aggressive',
               'funky', 'jazzy', 'shimmering', 'rising', 'falling', 'lofi', 'detuned', 'tonal', 'percussive'}
# words that say how something sounds, feels or what made it: kept as keywords when a file or
# folder name has them (song, kit and pack titles are full of other words that only add noise)
SOUND_WORDS = set('''
ethereal eerie tense tension sinister menacing ominous haunted haunting melancholy melancholic nostalgic
nostalgia euphoric euphoria happy lonely dreamy mysterious mystical mystic spooky creepy evil hypnotic angry
playful funny quirky weird strange bizarre dramatic intense energetic chilled tranquil serene gentle subtle
peaceful calm relaxed relaxing romantic sexy sultry spacey heroic triumphant victorious majestic hopeful
uplifting sad emotional moody tender intimate solemn sombre somber anxious nervous frantic chaotic
restless suspense suspenseful horror scary dread ghostly angelic heavenly celestial cosmic futuristic alien
crunchy crunch gritty grit grainy grain grains rough smooth glassy metallic wooden hollow thick thin fat beefy
punch punchy warm cold icy airy breathy fuzzy buzzy wonky wavy warped wobbly squelch squelchy bubbly
sparkling sparkle shimmer shimmering bright dull muffled distorted saturated compressed filtered gated
reversed chopped stuttered stutter stutters glitchy granular detuned modulated phased flanged tremolo vibrato
staccato legato sustained pizzicato resonant resonance atonal dissonant dissonance chromatic harmonized
syncopated triplet triplets shuffle shuffled swung offbeat rolling bouncy bouncing pumping pulsing rhythmic
percussive tonal textured textural cinematic organic natural synthetic digital analog analogue vintage lofi
dusty crackling crackle crackles rusty cassette mechanical robotic underwater distant roomy echo echoing
delayed massive huge heavy loud quiet tiny deep boomy subby snappy tight loose sloppy crisp crispy sharp
clean dirty filthy nasty brutal savage harsh noisy static interference hum hums buzz whoosh swish swipe whip
zap zaps laser lasers bleep bleeps beep beeps chirp ping ding clang clank clack click clicks tick ticks
knock thud thump thumps slam smack crack pop pops popping splat sizzle fizz fizzy rattle rattles rattling
creak creaky rumble rumbles roar growling scream screams screech screeches whistle whistles siren sirens
alarm heartbeat breathing laugh whisper whispers talking dialogue crowd birds bird water rain rainy wind
windy thunder storm fire ice glass wood metal metals paper plastic rubber stone stones sand gravel dust dirt
chain chains coins keyboard phone radio robot train engine motor car subway street kitchen household toy
toys clock spring springs tube amp transistor circuit voltage electricity sonar tape bend bends slides glide
twang picking strummed muted palm overdrive fuzz feedback wah chorus phaser flanger bitcrushed bitcrush
lowpass highpass sidechain sidechained pitched tuned untuned riser swell swells drone droning evolving
glitch noise atmosphere ambience ambient eight bit chiptune retro arcade hyper trippy psychedelic
industrial tribal ritual medieval ancient oriental exotic wild primal epic dark aggressive groovy funky
jazzy soulful bluesy gospel festival stadium anthem anthemic driving rising falling descending ascending
dorian phrygian lydian mixolydian aeolian locrian ionian pentatonic
jupiter polysix korg roland yamaha casio nord arturia sequential linn emu akai mpc ensoniq kawai hammond
rhodes wurlitzer clavinet mellotron theremin vocoder talkbox
'''.split())
# plain words people search for that the FX Name and Description of a CatID don't already say
SYNONYMS = {
    'DRMKick': ['Bass Drum'], 'DRMClap': ['Handclap'], 'DRMHat': ['Hihat'],
    'DRMCymb': ['Cymbal'], 'DRMTom': ['Tom Drum', 'Tomtom'], 'DRMRim': ['Rimshot', 'Sidestick'], 'DRMFill': ['Drum Fill'],
    'DRMBreak': ['Breakbeat'], 'DRMLoop': ['Drum Beat', 'Groove'], 'DRMTop': ['Percussion Top'],
    'PERCShak': ['Shaker'], 'PERCTamb': ['Tambourine'], 'PERCCowb': ['Cowbell'], 'PERCHand': ['Hand Drum'],
    'PERCLoop': ['Percussion'],
    'BASS808': ['Sub Bass'], 'BASSSub': ['Low End'], 'BASSSynth': ['Synth Bass'], 'BASSGrowl': ['Wobble'],
    'BASSElec': ['Bass Guitar'], 'BASSMisc': ['Bassline'], 'BASSUpright': ['Double Bass'],
    'SYNTHArp': ['Arpeggio'], 'SYNTHChord': ['Chords'], 'SYNTHPad': ['Synth Pad'],
    'SYNTHPluck': ['Synth Pluck'], 'SYNTHStab': ['Synth Stab'], 'SYNTHMisc': ['Synthesizer'],
    'SYNTHLead': ['Synth Lead', 'Melody'], 'FXMisc': ['Sound Design'], 'VOCLMisc': ['Voice'],
    'STEMMix': ['Mixdown', 'Instrumental'],
    'FXRiser': ['Uplifter', 'Build Up'], 'FXDown': ['Downsweep', 'Faller'], 'FXSweep': ['Whoosh'],
    'FXSubdrop': ['Sub Boom'], 'FXReverse': ['Reversed'], 'FXNoise': ['White Noise'], 'FXAtmos': ['Atmosphere'],
    'FXGlitch': ['Stutter'], 'FXScratch': ['Turntable'], 'FXImpact': ['Boom'],
    'VOCLChop': ['Vocal Chop'], 'VOCLAdlib': ['Ad Lib'], 'VOCLPhrase': ['Vocal Phrase'], 'VOCLRap': ['Rap Vocal'],
    'VOCLLead': ['Topline'], 'VOCLShout': ['Vocal Shout'], 'VOCLChoir': ['Choir'],
    'KEYSEpiano': ['Electric Piano'], 'KEYSOrgan': ['Organ'], 'KEYSPiano': ['Piano', 'Keys'],
    'GITRAco': ['Acoustic Guitar'], 'GITRElec': ['Electric Guitar'], 'GITRDist': ['Overdrive'],
    'SMPLVinyl': ['Crackle'], 'SMPLChop': ['Chop'],
    'TPRCMarimba': ['Mallet'], 'TPRCVibe': ['Mallet'], 'TPRCXylo': ['Mallet'], 'TPRCGlock': ['Bells'],
}

# Key spelling from the style guide: one name per pitch.
MAJOR = {'C': 'C', 'C#': 'Db', 'DB': 'Db', 'D': 'D', 'D#': 'Eb', 'EB': 'Eb', 'E': 'E', 'F': 'F', 'F#': 'F#',
         'GB': 'F#', 'G': 'G', 'G#': 'Ab', 'AB': 'Ab', 'A': 'A', 'A#': 'Bb', 'BB': 'Bb', 'B': 'B', 'CB': 'B'}
MINOR = {'C': 'Cmin', 'C#': 'C#min', 'DB': 'C#min', 'D': 'Dmin', 'D#': 'Ebmin', 'EB': 'Ebmin', 'E': 'Emin',
         'F': 'Fmin', 'F#': 'F#min', 'GB': 'F#min', 'G': 'Gmin', 'G#': 'G#min', 'AB': 'G#min', 'A': 'Amin',
         'A#': 'Bbmin', 'BB': 'Bbmin', 'B': 'Bmin'}
FULL = {'#': ' sharp', 'b': ' flat'}
KEY_RE = re.compile(r'^([a-g])(#|b|sharp|flat|s)?(m|min|minor|maj|major)?$', re.I)
ROOT_RE = re.compile(r'^([A-G])(#|b)?(-?[0-8])$')
ROOT_OK = re.compile(r'^([A-G])(#|b)?(-?[0-8])?$')
BPM_RE = re.compile(r'(?<![A-Za-z\d])(\d{2,3}(?:\.\d)?)\s*bpm|bpm\s*(\d{2,3})(?!\d)', re.I)

CAT_NOUN = {'DRUMS': 'drum', 'PERCUSSION': 'percussion', 'SYNTH': 'synth', 'BASS': 'bass', 'GUITAR': 'guitar',
            'ORCHESTRA': 'orchestra', 'VOCALS': 'vocal', 'SAMPLE': 'sample', 'TRACKS': 'track', 'STEM': 'stem'}
CAT_FIRST = {'SYNTH', 'VOCALS', 'SAMPLE', 'ORCHESTRA'}
NOUN = {'DRMLoop': 'drum loop', 'DRMFill': 'drum fill', 'DRMBreak': 'drum break', 'DRMTop': 'top loop',
        'DRMHat': 'hi-hat', 'DRMRim': 'rimshot', 'DRMSnap': 'finger snap', 'DRMClap': 'clap',
        'PERCLoop': 'percussion loop', 'TRKStinger': 'stinger', 'TRKJingle': 'jingle', 'STEMMix': 'full mix',
        'BASSElec': 'electric bass', 'BASSUpright': 'upright bass', 'KEYSEpiano': 'electric piano',
        'WWNDReed': 'free-reed instrument', 'VOCLLead': 'lead vocal', 'VOCLBacking': 'backing vocal'}


def initials_of(name):
    """Initials a pack code may use: "Adventures in Hip Hop" -> aihh, ahh; "AudeoBox" -> ab."""
    parts = re.findall(r'[A-Z][a-z]+|[a-z]+|[A-Z]+(?![a-z])', name)
    words = [p.lower() for p in parts]
    out = {''.join(w[0] for w in words), ''.join(w[0] for w in words if w not in FILLER)}
    return {i for i in out if i}


def drop_sequence(words, seq):
    """words without any run of them that spells seq ("overdrive", "audio"); seq of one word: that word."""
    if not seq:
        return list(words)
    out, i, n = [], 0, len(seq)
    words = list(words)
    while i < len(words):
        if words[i:i + n] == seq or (n > 1 and words[i] == ''.join(seq)):
            i += n if words[i:i + n] == seq else 1
            continue
        out.append(words[i])
        i += 1
    return out


def tokens(text):
    """Lowercase words of a file or folder name. More forgiving than the app: also splits on
    - . ( ) and between letters and digits ("Kick01" -> kick, 01), and keeps joined forms."""
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    out = []
    for part in re.split(r'[\s_.()\[\]{},+]+', text):
        if not part:
            continue
        low = part.lower()
        out.append(low)
        if '-' in low:
            out.append(low.replace('-', ''))
            out += [p for p in low.split('-') if p]
        split = re.findall(r'[a-z]+|\d+', low)
        if len(split) > 1 and not re.match(r'^\d+(bpm|s)$', low):
            out += split
    return out


def parse_key(words_orig):
    """Find a musical key in the original-case words.
    Returns (style-guide key, full name, the words that made up the key) or ('', '', set())."""
    for i, w in enumerate(words_orig):
        nxt = words_orig[i + 1].lower() if i + 1 < len(words_orig) else ''
        m = KEY_RE.match(w)
        if not m:
            continue
        if (m.group(2) or '').lower() == 'b' and not (w[0].isupper() and w[1] == 'b'):
            continue  # "BB", "AB", "bb" are codes; a flat key is written "Bb"
        if (m.group(2) or '').lower() == 's' and not (m.group(2) == 's' and m.group(3)):
            continue  # "DS", "Fs" are codes; "Csm" (C sharp minor) is the only "s" spelling kept
        if not m.group(2) and not m.group(3) and not w[0].isupper() and nxt not in ('major', 'minor', 'maj', 'min'):
            continue
        if m.group(3) == 'M' or (m.group(3) and not m.group(2) and not w[0].isupper()):
            continue  # "DM2", "fm": codes; a minor key is written "Dm" or "D#m"
        note, acc, qual = m.group(1).upper(), (m.group(2) or ''), (m.group(3) or '').lower()
        acc = {'sharp': '#', 's': '#', 'flat': 'b'}.get(acc.lower(), acc)
        if not qual and nxt in ('major', 'minor', 'maj', 'min'):
            qual = nxt
        # a lone letter (a, b, e...) is only a key when it is uppercase and next to a tempo or quality
        prev = words_orig[i - 1].lower() if i else ''
        tempo = lambda t: t.endswith('bpm') or (t.isdigit() and 60 <= int(t) <= 200)
        tempo_near = tempo(nxt) or tempo(prev)
        if not acc and not qual and not (w.isupper() and len(w) == 1 and tempo_near):
            if nxt not in ('major', 'minor', 'maj', 'min'):
                continue
        lookup = (note + acc).upper()
        minor = qual.startswith('m') and not qual.startswith('maj')
        key = (MINOR if minor else MAJOR).get(lookup)
        if not key:
            continue
        root = key.replace('min', '')
        full = root[0] + FULL.get(root[1:], '') + (' minor' if minor else ' major')
        used = {w.lower()} | ({nxt} if nxt in ('major', 'minor', 'maj', 'min') else set())
        return key, full, used
    return '', '', set()


def parse_bpm(stem, words, is_loop):
    m = BPM_RE.search(stem)
    if m:
        return m.group(1) or m.group(2)
    if is_loop:
        # a number on its own ("Loop_124_Am"), not one glued to a word ("SYNTH104" is an index)
        # and not a bar range ("147-149")
        for w in re.split(r'[\s_\-.()\[\]{},+#]+', re.sub(r'\d+-\d+', ' ', stem)):
            if w.isdigit() and len(w) == 3 and w.startswith('0') and 60 <= int(w) <= 99:
                return ''  # "C_Maj_080_44_27...": a zero-padded tempo; don't guess from the rest
            if w.isdigit() and 60 <= int(w) <= 200 and not w.startswith('0'):
                return w
        m = re.search(r'loop\s*(\d{2,3})(?!\d)', stem, re.I)  # "Perc Loop124"
        if m and 60 <= int(m.group(1)) <= 200:
            return m.group(1)
    return ''


def load_genres():
    genres = build_catalog.load_genres()
    lookup = {}
    for g in genres:
        lookup[re.sub(r'[^a-z0-9]', '', g['Subgenre'].lower().replace('&', 'and'))] = (g['Genre'], g['Subgenre'])
    for g in {g['Genre'] for g in genres}:
        lookup.setdefault(re.sub(r'[^a-z0-9]', '', g.lower().replace('&', 'and')), (g, ''))
    for ambiguous in ('swing', 'rage', 'experimental', 'industrial', 'ambient', 'hybrid', 'global', 'fantasy',
                      'chamber'):
        lookup.pop(ambiguous, None)  # in sample packs these describe groove or mood far more often
    lookup.update({'baile': ('Latin & Caribbean', 'Brazilian Funk'), 'dnb': ('Bass Music', 'Drum & Bass'), 'lofi': ('Hip Hop', 'Lo-Fi Hip Hop'),
                   'ukg': ('Bass Music', 'UK Garage'), 'rnb': ('R&B & Soul', 'R&B'), 'hiphop': ('Hip Hop', '')})
    return lookup


def find_genre(word_lists, lookup):
    """Longest genre name found in the file name first, then in the folder names."""
    for words in word_lists:
        words = [w for w in words if re.match(r'^[a-z0-9&]+$', w)]
        for n in (3, 2, 1):
            for i in range(len(words) - n + 1):
                key = ''.join(words[i:i + n]).replace('&', 'and')
                if key in lookup:
                    return lookup[key]
    return '', ''


ABBREV = {'brk': 'Break', 'bss': 'Bass', 'snr': 'Snare', 'kck': 'Kick', 'clp': 'Clap', 'pno': 'Piano', 'hh': 'Hi-Hat', 'gtr': 'Guitar', 'drm': 'Drum', 'gtrs': 'Guitars', 'syn': 'Synth', 'bsln': 'Bassline', 'oh': 'Open Hat', 'ch': 'Closed Hat', 'perc': 'Perc', 'fx': 'FX',
          'sfx': 'SFX', 'vox': 'Vox', 'ep': 'E-Piano', 'bd': 'Kick', 'sd': 'Snare', 'cym': 'Cymbal',
          'tamb': 'Tambourine', 'shkr': 'Shaker', 'hho': 'Open Hat', 'hhc': 'Closed Hat', 'snth': 'Synth', 'chd': 'Chord', 'cng': 'Conga', 'fullmix': 'Full Mix',
          'hihat': 'Hi-Hat', 'hihats': 'Hi-Hat', 'kik': 'Kick', 'prc': 'Perc', 'mus': 'Music', 'elec': 'Electric',
          'ens': 'Ensemble', 'stacc': 'Staccato', 'stac': 'Staccato', 'seq': 'Sequence', 'org': 'Organ',
          'percs': 'Perc', 'atmo': 'Atmos', 'leadvox': 'Lead Vox', 'amb': 'Ambient', 'orch': 'Orchestra'}
DESC_WORDS = {'Perc': 'percussion', 'Vox': 'vocal', 'Gtr': 'guitar', 'Synth': 'synth', 'Hihat': 'hi-hat',
              'Bassdrum': 'bass drum', 'Hat': 'hi-hat', 'Leadvox': 'lead vocal'}
# how joined or shortened words are written in an FX Name (display only, not used for matching)
FX_SPELL = {'cl': 'Closed', 'op': 'Open', 'shake': 'Shaker', 'shakes': 'Shaker', 'shakey': 'Shaker',
            'shakerz': 'Shaker', 'clapz': 'Clap', 'kickz': 'Kick', 'snarez': 'Snare', 'hatz': 'Hat', 'percz': 'Perc',
            'sanre': 'Snare', 'cloased': 'Closed', 'ful': 'Full', 'voc': 'Vocal', 'vocs': 'Vocal', 'fem': 'Female', 'ohh': 'Open Hat', 'ohat': 'Open Hat',
            'openhat': 'Open Hat', 'closedhat': 'Closed Hat', 'clhat': 'Closed Hat', 'fxloop': 'FX',
            'synthpad': 'Synth Pad', 'subbass': 'Sub Bass', 'snaredrum': 'Snare', 'kickdrum': 'Kick',
            'pizz': 'Pizzicato', 'clav': 'Clavinet', 'melo': 'Melody', 'digi': 'Digital', 'fx': 'FX',
            'synthlead': 'Synth Lead', 'synthbass': 'Synth Bass', 'vocalchop': 'Vocal Chop', '8bit': '8-Bit'}
NEGATED_RE = re.compile(r'^no-?(kick|snare|hat|clap|bass|drum|vocal|vox|perc|sub|cymbal|top)s?$')
FILLER = {'into', 'the', 'of', 'and', 'with', 'to', 'a', 'an', 'in', 'on'}
TOOLS = {'elevenlabs': 'ElevenLabs', 'suno': 'Suno', 'udio': 'Udio', 'stableaudio': 'Stable Audio',
         'audiogen': 'AudioGen', 'audiocraft': 'AudioCraft', 'audioldm': 'AudioLDM', 'musicgen': 'MusicGen'}
TRACK_WORDS = {'track', 'tracks', 'song', 'songs', 'music', 'bgm', 'soundtrack', 'ost', 'score', 'cue', 'cues',
               'theme', 'themes', 'stinger', 'stingers', 'jingle', 'jingles', 'full', 'instrumental'}
# Role words that describe one variant: they only weigh half ("Open" also fits a cymbal).
VARIANT_WORDS = {'open', 'closed', 'pedal', 'clean', 'muted', 'mute', 'soft', 'hard', 'short', 'long', 'white',
                 'pink', 'brown', 'dark', 'bright', 'full', 'double', 'steel', 'felt', 'prepared', 'grand',
                 'upright', 'french', 'tenor', 'dist', 'spanish', 'drop', 'drops', 'alto', 'soprano', 'baritone', 'electric', 'acoustic', 'jazz',
                 'slide', 'classical', 'spanish', 'concert', 'digital', 'synthetic', 'orchestral', 'egg',
                 'brush', 'brushes'}
# Words that occur in almost every music file name; they only break ties.
GENERIC = {'loop', 'loops', 'hit', 'hits', 'oneshot', 'oneshots', 'one-shot', 'fx', 'misc', 'sample', 'samples',
           'sound', 'sounds', 'riff', 'riffs', 'full', 'stem', 'stems', 'groove', 'grooves', 'beat', 'beats',
           'melodic', 'melody', 'melodies', 'music', 'musical', 'musicloop', 'musicloops', 'melodyloop',
           'melodicloop'}
CORE_NOUNS = {'kick', 'kicks', 'snare', 'snares', 'clap', 'claps', 'hat', 'hats', 'hihat', 'perc', 'tom', 'toms',
              'crash', 'ride', 'rim', 'shaker', 'bass', 'synth', 'pad', 'pads', 'lead', 'pluck', 'stab', 'vox',
              'vocal', 'vocals', 'chord', 'chords', 'keys', 'piano', 'guitar', 'gtr', 'riser', 'impact', 'sweep',
              'fill', 'arp', 'organ', 'strings', 'brass', 'flute', 'choir', 'cymbal', 'conga', 'bongo', '808',
              'percussion', 'tambourine', 'cowbell', 'triangle', 'trumpet', 'sax', 'saxophone', 'violin', 'cello',
              'drum', 'drums', 'bassdrum', 'bassdrums'}
TRACK_FOLDER = {'tracks', 'songs', 'full', 'length', 'lengths', 'mixes', 'versions', 'music', 'themes', 'stingers',
                'jingles', 'cues', 'bgm', 'soundtrack', 'ost', 'demo', 'demos'}
ALIASES = {'shake': 'shaker', 'shakes': 'shaker', 'shakey': 'shaker', 'shakerz': 'shaker', 'sanre': 'snare',
           'cloased': 'closed', 'bs': 'bass', 'upfilter': 'sweep', 'downfilter': 'sweep', 'sn': 'snare', 'cng': 'conga', 'songstarter': 'fullmix', 'songstarters': 'fullmix', 'rise': 'riser', 'rises': 'riser', 'org': 'organ', 'chd': 'chord', 'chds': 'chords', 'snth': 'synth', 'synt': 'synth', 'lp': 'loop', 'lps': 'loops', 'mus': 'music', 'faller': 'downlifter', 'fallers': 'downlifter',
           'hho': 'openhat', 'hhc': 'closedhat', 'downshift': 'downlifter', 'downshifter': 'downlifter', 'downshifters': 'downlifter',
           'ambiance': 'atmos', 'ambiances': 'atmos', 'ambience': 'atmos', 'ambiences': 'atmos', 'acap': 'acapella', 'pluk': 'pluck', 'plk': 'pluck',
           'brk': 'break', 'bss': 'bass', 'bsln': 'bassline', 'syn': 'synth', 'kck': 'kick', 'kik': 'kick', 'snr': 'snare',
           'clp': 'clap', 'hh': 'hihat', 'hht': 'hihat', 'oh': 'openhat', 'ch': 'closedhat', 'gtr': 'guitar',
           'gtrs': 'guitar', 'pno': 'piano', 'drm': 'drum', 'drms': 'drums', 'vox': 'vocal', 'voc': 'vocal',
           'ld': 'lead', 'pd': 'pad', 'arp': 'arp', 'fx': 'fx', 'sfx': 'fx', 'perc': 'perc', 'prc': 'perc',
           'tom': 'tom', 'rim': 'rim', 'cym': 'cymbal', 'crsh': 'crash', 'shkr': 'shaker', 'tamb': 'tambourine',
           'brs': 'brass', 'str': 'strings', 'strs': 'strings', 'orch': 'orchestra', 'sub': 'sub'}
ONE_SHOT_TYPES = {'DRMKick', 'DRMSnare', 'DRMClap', 'DRMSnap', 'DRMHat', 'DRMCymb', 'DRMTom', 'DRMRim',
                  'PERCHand', 'PERCShak', 'PERCTamb', 'PERCCowb', 'PERCBlock', 'PERCScrp', 'PERCTri', 'PERCOrch',
                  'PERCElec', 'PERCBody', 'PERCFound', 'PERCSleigh', 'PERCMisc', 'FXImpact', 'FXSubdrop'}
ACRONYMS = {'ukg', 'fx', 'sfx', 'dj', 'mc', 'bv', 'ai', 'uk', 'edm', 'tr', 'fm', 'am', 'vhs', 'tv', 'cd', 'eq', 'lfo',
            'dnb', 'idm', 'ebm', 'rnb', 'nyc', 'la', 'usa', 'ep', 'sp', 'mpc', 'sp1200', 'vst'}
FAMILY_TITLE = {'DRUMS': 'Drum', 'PERCUSSION': 'Perc', 'TUNED PERCUSSION': 'Mallet', 'KEYS': 'Keys',
                'SYNTH': 'Synth', 'BASS': 'Bass', 'GUITAR': 'Guitar', 'STRINGS': 'Strings', 'BRASS': 'Brass',
                'WOODWINDS': 'Woodwind', 'ORCHESTRA': 'Orchestra', 'VOCALS': 'Vocal', 'WORLD': 'World',
                'SAMPLE': 'Sample', 'FX': 'FX', 'TRACKS': 'Track', 'AI GENERATED': 'AI Sound'}
CHORD_RE = re.compile(r'^(maj|min|sus|aug|dim|add|m)\d{1,2}$|^(\d{1,2})(th|maj|min|sus)$|^(sus|aug|dim)$', re.I)
VOCAL_CONTEXT = {'vocal', 'vocals', 'vox', 'voice', 'voices', 'sung', 'singer', 'singing', 'acapella', 'acappella',
                 'rap', 'raps', 'choir', 'adlib', 'adlibs', 'chant', 'chants', 'shout', 'shouts', 'beatbox', 'vocoder',
                 'whisper', 'breath', 'spoken', 'lyrics', 'hook', 'hooks', 'harmony', 'harmonies', 'backing', 'bv',
                 'bvs', 'vocalchop', 'vocalchops', 'female', 'male', 'acap'}
COMMON_SHARE = 0.01  # a word in more than 1 % of all files is too common to be a useful keyword
STEM_WORDS = {'stem', 'stems', 'multitrack', 'multitracks', 'construction', 'constructionkit', 'kit', 'kits',
              'songstarter', 'songstarters'}
SHORT_OK = {'hh', 'oh', 'ch', 'bd', 'sd', 'ep', 'fx', 'dj', 'mc', 'bv', 'ai'}
MACHINES = {'808', '909', '707', '606', '303'}
KEEP_PLURAL = {'strings', 'keys', 'chimes', 'bells', 'woodwinds', 'drums', 'vibes', 'brass', 'bongos', 'congas',
               'timbales', 'claves', 'maracas', 'cymbals', 'brushes', 'sticks', 'mallets', 'bass'}
LOOP_WORDS = {'loop', 'loops', 'beat', 'beats', 'groove', 'grooves'}
SHOT_WORDS = {'oneshot', 'oneshots', 'one-shot', 'one-shots', 'hit', 'hits', 'single', 'singles', 'shot', 'shots'}
LOOP_ORDER = ['DRMLoop', 'PERCLoop', 'SMPLLoop', 'DRMTop', 'DRMBreak']
LOOP_TYPES = set(LOOP_ORDER)
FOLEY_WORDS = {'foley', 'footstep', 'footsteps', 'sfx', 'fx', 'ambience', 'ambiance', 'field', 'household',
               'objects', 'object', 'recording', 'recordings', 'nature', 'animals', 'animal'}
FAMILY_LOOP = {'DRUMS': 'DRMLoop', 'PERCUSSION': 'PERCLoop'}
# folder words that name an instrument family: a file in "Rap Vocals" or "Piano" is in that family
FAMILY_DIR = {'DRUMS': {'drum', 'drums', 'drumloops', 'drumloop', 'beat', 'beats'}, 'PERCUSSION': {'percussion', 'percs', 'perc'},
              'BASS': {'bass', 'basses', 'basslines', 'bassline'}, 'SYNTH': {'synth', 'synths'},
              'KEYS': {'keys', 'piano', 'pianos'}, 'GUITAR': {'guitar', 'guitars'}, 'VOCALS': {'vocal', 'vocals', 'vox'},
              'STRINGS': {'strings', 'violin', 'violins', 'cello', 'cellos'},
              'BRASS': {'brass', 'horns', 'trumpet', 'trumpets', 'trombone', 'trombones'},
              'WOODWINDS': {'woodwinds', 'winds', 'sax', 'saxophone', 'saxophones', 'flute', 'flutes', 'clarinet'},
              'FX': {'fx', 'sfx', 'effects'}}
FAMILY_DIR['DRUMS'] |= {'kick', 'kicks', 'snare', 'snares', 'hat', 'hats', 'hihat', 'hihats', 'clap', 'claps',
                        'cymbal', 'cymbals', 'crash', 'crashes', 'ride', 'rides', 'tom', 'toms', 'rim', 'rims',
                        'rimshot', 'rimshots', 'snap', 'snaps', 'bassdrum', 'bassdrums', 'fill', 'fills'}
FAMILY_DIR['PERCUSSION'] |= {'percussions', 'shaker', 'shakers', 'conga', 'congas', 'bongo', 'bongos', 'tambourine',
                             'tambourines', 'cowbell', 'cowbells'}
FAMILY_DIR['SYNTH'] |= {'pad', 'pads', 'pluck', 'plucks', 'arp', 'arps'}
FAMILY_DIR['PERCUSSION'] |= {'maracas', 'guiro', 'claves', 'woodblock', 'triangle'}
AMBIGUOUS_PARTS = {'ride', 'rides', 'fill', 'fills', 'snap', 'snaps', 'crash', 'crashes', 'rim', 'rims', 'hat',
                   'impact', 'transition', 'transitions'}  # also lyrics or FX words
FAMILY_DIR['VOCALS'] |= {'acapella', 'acapellas', 'adlib', 'adlibs', 'vocalchops'}
FAMILY_DIR['FX'] |= {'riser', 'risers', 'impact', 'impacts', 'sweep', 'sweeps', 'downlifter', 'downlifters',
                     'transition', 'transitions', 'uplifter', 'uplifters'}
FAMILY_DIR['KEYS'] |= {'organ', 'organs', 'rhodes', 'epiano'}
FAMILY_NOUN = {'BASS': ('Bass', {'bass', 'basses', '808', 'bassline'}),
               'GUITAR': ('Guitar', {'guitar', 'guitars', 'banjo', 'ukulele', 'uke', 'mandolin'})}
BARS_RE = re.compile(r'^(\d{1,2})\s*bars?$', re.I)


def source_id(pack):
    """Short uppercase SourceID from the pack folder: "Lofi Dreams" -> LOFIDREAMS,
    "Trap Essentials Vol 2" -> TEV2."""
    parts = re.findall(r'[A-Za-z]+|\d+', pack)
    joined = ''.join(parts).upper()
    initials = ''.join(p[0] if p.isalpha() else p for p in parts).upper()
    if len(joined) <= 12:
        return joined or 'SOURCE'
    return initials if len(initials) >= 3 else joined[:12]


class Suggester:
    def __init__(self, creator, pack_depth=1, prefer='music'):
        self.pack_depth = pack_depth
        self.prefer = prefer
        _, rows = build_catalog.load()
        self.rows = {r['CatID']: r for r in rows}
        self.matcher = build_catalog.Matcher(rows)
        self.genres = load_genres()
        self.creator = creator
        # words used to split joined spellings ("bassdrum" -> Bass Drum): music keywords only
        self.music_words = {w for r in rows if r['_custom'] and r['CatShort'] != 'AI'
                            for w in self.matcher.keywords[r['CatID']] if len(w) >= 3}
        self.music_vocab = {w for r in rows if r['_custom'] and r['CatShort'] != 'AI'
                            for w in self.matcher.keywords[r['CatID']]}
        by_cat = collections.defaultdict(list)
        for r in rows:
            by_cat[r['Category']].append(self.matcher.keywords[r['CatID']])
        # family words: in at least half of a category's subcategories
        self.family = {}
        for cat, sets in by_cat.items():
            count = collections.Counter(w for s in sets for w in s)
            self.family[cat] = {w for w, n in count.items() if len(sets) > 1 and n * 2 >= len(sets)}
        self.used = collections.Counter()
        self.names = set()
        self.derived = set()
        self.short_alias = set()
        self.genre_tokens = {w for g in build_catalog.load_genres() for w in
                             re.split(r'[^a-z0-9]+', (g['Genre'] + ' ' + g['Subgenre']).lower()) if len(w) > 2}
        self.genre_tokens |= set(self.genres) - {''}
        self.root = None
        # plain English words (lowercase dictionary words, so no first names): "Ethereal" is a word,
        # "Schay" or "Dabow" is a producer or kit name
        english = os.path.join(os.path.dirname(os.path.abspath(build_catalog.__file__)), '..', 'catalog',
                               'english_words.txt')
        with open(english, encoding='utf-8') as f:
            self.english = {w.strip() for w in f if w.strip()}
        # first names and places ("Jon Casey", "Toby", "Kristine"): producer and kit names, not sounds
        with open(os.path.join(os.path.dirname(english), 'proper_names.txt'), encoding='utf-8') as f:
            self.names_list = {w.strip() for w in f if w.strip()}
        # word -> CatIDs, so a file is only scored against CatIDs sharing a word with it
        self.index = collections.defaultdict(list)
        for catid, kws in self.matcher.keywords.items():
            for w in kws:
                self.index[w].append(catid)
        self.catids = set(self.matcher.keywords)
        # words two or more subcategories of the same category share ("drum" in DRUMS) count once,
        # words only one subcategory has ("kick") count double
        per_cat = collections.defaultdict(collections.Counter)
        for r in rows:
            per_cat[r['Category']].update(self.matcher.keywords[r['CatID']])
        # a word shared inside any category ("synth" in SYNTH) counts once everywhere, so
        # "Synth Snare" stays a snare instead of becoming BASS/SYNTH
        self.shared_by_cat = {cat: {w for w, n in c.items() if n >= 2} for cat, c in per_cat.items()}
        self.shared = set().union(*self.shared_by_cat.values())
        self.music_cats = {r['Category'] for r in rows if r['_custom'] and r['CatShort'] != 'AI'}
        self.sub_words = {c: set(re.findall(r'[a-z0-9]+', self.rows[c]['SubCategory'].lower())) for c in self.catids}
        self.misc_of = {r['Category']: r['CatID'] for r in rows if r['_custom'] and r['SubCategory'] == 'MISC'}
        self.catid_lengths = sorted({len(c) for c in self.catids}, reverse=True)
        # genre words that are not also instrument words ("jungle", "disco"; not "bass", "synth", "drum")
        instrument_words = CORE_NOUNS | {w for ws in FAMILY_DIR.values() for w in ws} | set(ALIASES.values()) | {
            w for c in self.catids if self.rows[c]['Category'] in self.music_cats - {'TRACKS', 'STEM'}
            for w in self.sub_words[c]}
        instrument_words |= {w + 's' for w in instrument_words}
        self.instrument_words = instrument_words
        self.weak_genre = self.genre_tokens - instrument_words
        # subcategory names only one CatID has ("chord" -> SYNTHChord, "piano" -> KEYSPiano) break ties
        family_names = {w for c in self.music_cats for w in re.findall('[a-z]+', c.lower())} | {
            'misc', 'loop', 'fx', 'voice', 'body', 'found', 'block', 'hit', 'ensemble', 'processed', 'electronic',
            'top', 'mix', 'sound'}
        sub_count = collections.Counter(frozenset(self.sub_words[c]) for c in self.catids if self.rows[c]['_custom'])
        self.sub_bonus = {c: self.sub_words[c] for c in self.catids
                          if self.rows[c]['Category'] in self.music_cats and self.sub_words[c]
                          and sub_count[frozenset(self.sub_words[c])] == 1 and not self.sub_words[c] & family_names}

    def expand(self, words):
        """Add joined pairs ("bass line" -> bassline) and known word endings of unknown words
        ("nastyclap" -> clap, "bigkick" -> kick)."""
        known = lambda w: w in self.index or w in ALIASES
        out = list(words)
        alpha = [w for w in words if w.isalpha()]
        out += [a + b for a, b in zip(alpha, alpha[1:]) if a + b in self.index or a + b in ALIASES]
        for w in alpha:
            if CHORD_RE.match(w):
                out.append('chord')  # "Maj7", "Sus4": a chord, so a chordal instrument
            elif w.endswith('z') and len(w) > 3 and w not in self.index and (w[:-1] in self.index or w[:-1] + 's' in self.index):
                out.append(w[:-1] if w[:-1] in self.index else w[:-1] + 's')  # "Clapz" -> clap, "Kickz" -> kick
            elif w.endswith('s') and len(w) > 3 and w not in self.index and w[:-1] in self.index:
                out.append(w[:-1])  # "downsweeps" -> downsweep
            elif len(w) >= 5 and not known(w) and w not in self.english:
                for i in range(2, len(w) - 1):
                    left, right = w[:i], w[i:]
                    instrument = lambda x: x in CORE_NOUNS or x in ALIASES or x in LOOP_WORDS or x in GENERIC
                    if known(left) and known(right) and (min(len(left), len(right)) >= 3 or
                                                         {left, right} & {'lp', 'fx', 'lps'}) \
                            and (instrument(left) or instrument(right)):  # not "teleport" -> tele + port
                        out += [left, right]  # "drumlp" -> drum, lp; "fxlp" -> fx, lp ("strpd" is not str + pd)
                        joined = ALIASES.get(left, left) + ALIASES.get(right, right)
                        if joined in self.index:
                            out.append(joined)  # "musiclp" -> musicloop
                        break
                else:
                    for i in range(2, len(w) - 2):
                        if w[i:] in CORE_NOUNS:
                            out.append(w[i:])  # "nastyclap" -> clap
                            break
        aliased = [ALIASES[w] for w in out if w in ALIASES]
        self.short_alias.update(ALIASES[w] for w in out if w in ALIASES and len(w) <= 2)
        out += aliased
        self.derived.update(w for w in out if w not in words)
        return out

    def drop_genre_phrases(self, words):
        """Remove multi-word genre names ("Future Bass", "Drum & Bass", "Deep House") so their
        instrument words don't count as instruments."""
        words = list(words)
        clean = [w for w in words if re.match(r'^[a-z0-9&]+$', w)]
        drop = set()
        for n in (3, 2):
            for i in range(len(clean) - n + 1):
                key = ''.join(clean[i:i + n]).replace('&', 'and')
                if key in self.genres and not {*clean[i:i + n]} <= drop:
                    drop |= set(clean[i:i + n])
        if not drop:
            return words
        return [w for w in words if w not in drop]

    def compound(self, w):
        """Split a joined word into two known words ("synthloop" -> synth, loop), or []."""
        known = lambda x: x in self.index or x in ALIASES
        if len(w) >= 5 and w.isalpha() and not known(w) and w not in self.english:
            for i in range(2, len(w) - 1):
                if known(w[:i]) and known(w[i:]) and len(w[:i]) >= 3 and (len(w[i:]) >= 3 or w[i:] in ('lp', 'fx')):
                    return [ALIASES.get(w[:i], w[:i]), ALIASES.get(w[i:], w[i:])]
        return []

    def already_ucs(self, name):
        # the longest CatID the name starts with, followed by "_". All-uppercase CatIDs such as
        # RAW, MIX or ADR are skipped: in sample packs they are almost always pack codes
        for n in self.catid_lengths:
            if name[:n] in self.catids and name[n:n + 1] == '_' and not name[:n].isupper():
                return name[:n]
        return None

    @staticmethod
    def scoring_words(words, exclude=frozenset()):
        return [w for w in words if (len(w) > 2 or w in SHORT_OK) and (not w.isdigit() or w in MACHINES)
                and w not in NOISE and w not in exclude]

    def choose(self, file_words, dir_words, pack_words, is_loop, self_dirs=(), publisher_words=(), tonal=False,
               custom_only=False, codes=(), one_shot=False):
        """Pick a CatID. Each matching word scores 2 when only this subcategory of its category has
        it ("kick"), 1 when several do ("drum"), 0.25 when it is generic ("loop"). Folder words count
        half. File names naming the subcategory ("Piano") get a bonus. Official UCS counts half in a
        music library, and loops only get music categories. Ties: the CatID matching the earliest
        file-name word, then the family's MISC, then music before official UCS."""
        has_ai = bool(AI_MARKERS & (set(file_words) | set(dir_words) | set(pack_words)))
        # pack titles are often repeated in file names ("Cymatics - Jet Ski - ... Lead"): don't score them
        title = (set(pack_words) - self.music_vocab) | set(publisher_words) | set(codes) | {
            ALIASES[c] for c in codes if c in ALIASES}
        fw = set(self.scoring_words(file_words, title))
        dw = set(self.scoring_words(dir_words, title))
        vocal = bool(VOCAL_CONTEXT & (set(file_words) | set(dir_words) | set(pack_words)))
        derived = self.derived
        pw = set(self.scoring_words(pack_words[-1:] and pack_words)) - fw - dw
        # the nearest folder that names an instrument family ("Rap Vocals", "Piano", "FX")
        near_family = set()
        for d in reversed(self_dirs[self.pack_depth:]):
            near_family = {cat for cat, ws in FAMILY_DIR.items() if ws & set(tokens(d))}
            if re.search(r'bass\s*drums?', d, re.I):
                near_family = (near_family - {'BASS'}) | {'DRUMS'}  # "Bass Drums" is kicks
            if near_family:
                break
        file_family = {cat for cat, ws in FAMILY_DIR.items() if (ws - AMBIGUOUS_PARTS) & set(file_words)}
        # "Your Type Beats" is a pack of instrumentals, not of drums
        pack_family = {cat for cat, ws in FAMILY_DIR.items() if (ws - {'beat', 'beats'}) & set(pack_words)}
        file_set = set(file_words) | {w[:-1] for w in file_words if w.endswith('s')}
        dir_set = set(dir_words) | {w[:-1] for w in dir_words if w.endswith('s')}
        position = {}
        for i, w in enumerate(file_words):
            position.setdefault(w, i)

        def score_all(fw, dw, pw, factor=1.0):
            scores = {}
            # TRACKS needs a track word in the file name or a folder called e.g. "Full Tracks"
            track_words = TRACK_WORDS & (set(file_words) - derived)
            if 'songstarter' in file_words or 'songstarters' in file_words:
                track_words -= {'song', 'songs'}  # "Song Starter": a kit mix, not a finished song
            if re.search(r'\b(track|song)s?\s*\d', ' '.join(file_words)):
                track_words -= {'track', 'song'}  # "Track02_Beat": a song number in a kit, not a finished track
            if 'loop' in file_words or 'loops' in file_words:
                track_words -= {'full', 'music'}  # a "full loop" or "music loop" is a kit loop, not a track
            track = track_words or any(set(tokens(d)) <= TRACK_FOLDER for d in self_dirs)
            stem = STEM_WORDS & (set(file_words) | set(dir_words) | set(pack_words))
            for catid in {c for w in fw | dw | pw for c in self.index.get(w, ())}:
                row = self.rows[catid]
                if catid.startswith('AI') and not has_ai:
                    continue
                if catid.startswith('TRK') and not track:
                    continue  # genre words alone don't make a file a finished track
                if is_loop and not row['_custom'] and row['Category'] != 'MUSICAL':
                    continue  # a loop is music
                if catid.startswith('STEM') and one_shot:
                    continue  # "Perc Hit" in a construction kit is a one-shot, not a stem
                if catid.startswith('STEM') and not stem and not (catid == 'STEMMix' and {'fullmix', 'mixdown'} & (
                        set(file_words) | set(dir_words))):
                    continue  # stems need "stem", "multitrack" or "construction kit" in the path
                if row['Category'] == 'ARCHIVED' or (custom_only and not row['_custom']):
                    continue  # ADR, RAW, MIX... are admin buckets, not sound types
                if catid == 'FXSubdrop' and not {'sub', 'subdrop', 'subdrops', 'boom', 'booms', 'downer'} & (
                        set(file_words) | set(dir_words)) and 'FX' not in near_family | pack_family:
                    continue  # "Drop Lead", "Turn_it_up_Drop2": the drop of a song, not a sub drop
                if catid == 'TPRCSteel' and not {'steel', 'steeldrum', 'steeldrums', 'steelpan', 'steelpans', 'pan',
                                                 'pans'} & (set(file_words) | set(dir_words) | set(pack_words)):
                    continue  # a steel drum, not any drum
                if catid == 'DRMFill' and file_family - {'DRUMS', 'PERCUSSION'}:
                    continue  # "Guitar Fill": a guitar
                if row['Category'] == 'VOCALS' and not vocal:
                    continue  # "Lead Loop" is a synth lead unless a vocal word says otherwise
                kws, shared = self.matcher.keywords[catid], self.shared
                def weight(w, cat=row['Category']):
                    if w == 'fx' and cat == 'FX':
                        return 1
                    if w in GENERIC:
                        return 0.25
                    if w in VARIANT_WORDS or w in self.weak_genre:
                        return 0.5  # "Jungle Atmos" is an atmosphere, "Spanish" a describing word
                    base = 1 if w in shared or len(w) <= 2 or w in self.short_alias else 2  # "OH", "SD": short codes count less
                    return base * 0.5 if w in derived and w not in CORE_NOUNS else base
                s = (sum(weight(w) for w in fw & kws) + 0.5 * sum(weight(w) for w in dw & kws)
                     + 0.1 * sum(weight(w) for w in pw & kws))
                sub = self.sub_bonus.get(catid)
                if sub and sub <= file_set:
                    s += 0.1  # the file names the subcategory ("Piano"): tie-breaker only
                elif sub and sub <= file_set | dir_set:
                    s += 0.05
                elif sub and sub <= set(pack_words):
                    s += 0.02  # "Soul Jazz Piano": a piano, not an electric piano
                if row['Category'] in near_family and (not file_family or row['Category'] in file_family
                                                       or row['Category'] == 'VOCALS'):
                    # in a "Rap Vocals" or "Piano" folder: that family (vocal file names are lyrics, so more),
                    # unless the file itself names another family ("Postcards - Bass" in Guitar Loops)
                    s += 1 if row['Category'] == 'VOCALS' else 0.75
                elif row['Category'] in pack_family and not near_family and not file_family and \
                        not CORE_NOUNS & set(file_words):
                    s += 0.75  # in a pack called "Vintage Drum Breaks" or "Soul Jazz Piano"
                if self.prefer == 'music' and not row['_custom']:
                    s *= 0.33
                elif self.prefer == 'sfx' and row['_custom'] and row['Category'] != 'AI GENERATED':
                    s *= 0.5
                if s >= 0.2:
                    first = min((position.get(w, 99) for w in fw & kws if w not in GENERIC), default=99)
                    specific = any(w not in GENERIC and w not in shared for w in fw & kws)
                    # words that define this family ("synth" for SYNTH) beat the same word used as
                    # a modifier elsewhere ("synth" in BASS/SYNTH)
                    family = sum(1 for w in (fw | dw) & kws if w in self.shared_by_cat[row['Category']])
                    core = any(w in CORE_NOUNS for w in fw & kws)
                    scores[catid] = (s * factor, first, specific, family, core)
            return scores

        scores = {c: v for c, v in score_all(fw, dw, pw).items() if (fw | dw) & self.matcher.keywords[c]}
        if one_shot:  # "Drum Hits/Mid Elements 53" is not a drum loop
            scores = {c: v for c, v in scores.items() if c not in LOOP_TYPES}
        from_pack = False
        # only describing words matched ("Dist" in "Mic3_DeskDist" of Vintage Drum Breaks): the pack
        # name knows the instrument better
        alias_targets = set(ALIASES.values())
        strong = lambda c: any(w not in VARIANT_WORDS and (w not in derived or w in CORE_NOUNS or w in alias_targets)
                               for w in (fw | dw) & self.matcher.keywords[c])
        if scores and not any(strong(c) for c in scores):
            saved = scores
            scores = {}
        else:
            saved = None
        if not scores and is_loop and {'melodic', 'melodics', 'melody', 'melodies', 'music'} & dw:
            return 'SMPLLoop', [], 'medium: music loop, instrument not named'
        if not scores:
            custom_only = True  # last resort: the pack name, music categories only
            pack_set = set(self.scoring_words(pack_words)) - {'dj', 'mc'} - (GENERIC - {'fx'}) - self.genre_tokens
            scores = score_all(pack_set, set(), set(), 0.5)
            # "Spanish" alone doesn't make a nylon guitar; a pack name never makes a track or a stem
            scores = {c: v for c, v in scores.items() if not c.startswith(('TRK', 'STEM'))
                      and any(w not in VARIANT_WORDS for w in pack_set & self.matcher.keywords[c])}
            from_pack = bool(scores)
            if not scores and saved:
                scores, from_pack = saved, False
        loop_default = 'SMPLLoop'
        if is_loop and scores:
            best = max(v[0] for v in scores.values())
            tied = {self.rows[c]['Category'] for c, v in scores.items() if v[0] == best}
            named = {cat for cat in tied if self.shared_by_cat.get(cat, set()) & fw}
            if len(tied) > 2 and len(named) == 1:  # "SYNTH073_HARDT" in a Keys folder: the file says synth
                scores = {c: v for c, v in scores.items() if self.rows[c]['Category'] in named}
        if is_loop and (not scores or len({self.rows[c]['Category'] for c, v in scores.items()
                                           if v[0] == max(x[0] for x in scores.values())}) > 2):
            if len(pack_family) == 1 and next(iter(pack_family)) in FAMILY_LOOP:
                # "Minimal Techno Drum Loops/100_MTDL_034": the pack says drum loop
                return FAMILY_LOOP[next(iter(pack_family))], [], 'medium: instrument from the pack name'
            return loop_default, [], 'medium: music loop, instrument not named'
        if not scores:
            return None, [], 'REVIEW: no match'
        best = max(v[0] for v in scores.values())
        top = [c for c, v in scores.items() if abs(v[0] - best) < 1e-9]
        percussive = lambda c: tonal and self.rows[c]['Category'] in ('DRUMS', 'PERCUSSION')
        if self.prefer == 'music':
            # "glitch hat": the instrument noun beats the describing FX word
            top.sort(key=lambda c: (not self.rows[c]['_custom'], is_loop and c not in LOOP_TYPES, percussive(c),
                                    not scores[c][4], -scores[c][3], scores[c][1], c))
        else:
            top.sort(key=lambda c: (scores[c][1], not self.rows[c]['_custom'], -scores[c][3], c))
        if top[0] == 'SMPLLoop' and not from_pack and not any(
                w not in GENERIC for w in (fw | dw) & self.matcher.keywords['SMPLLoop']):
            # only "melody"/"music" matched: "Ultimate Strings Melodies/Melody20Bpm85KeyG" is strings
            fam = near_family or pack_family
            if len(fam) == 1:
                cat = next(iter(fam))
                target = FAMILY_LOOP.get(cat) or self.misc_of.get(cat)
                if target and target != 'SMPLLoop':
                    return target, top[:5], 'medium: instrument from the folder or pack name'
        if self.prefer == 'music' and not self.rows[top[0]]['_custom'] and not from_pack:
            # an official sound-effect word ("Kissing Fish" -> fish market) in a music folder or pack: the
            # folder or pack name ("Cinematic Percussion", "Alien Guitars") knows better, unless it is foley
            words_here = set(file_words) | set(dir_words) | set(pack_words)
            fam = near_family or (pack_family if not FOLEY_WORDS & words_here else set())
            if len(fam) == 1:
                cat = next(iter(fam))
                target = FAMILY_LOOP[cat] if is_loop and cat in FAMILY_LOOP else self.misc_of.get(cat)
                if target:
                    return target, top[:5], 'medium: instrument from the folder or pack name'
        if from_pack:
            misc = [c for c in top if c.endswith('Misc')]
            one_family = len({self.rows[c]['Category'] for c in top}) == 1
            loops = sorted((c for c in top if c in LOOP_TYPES), key=LOOP_ORDER.index)
            if is_loop and loops and one_family:
                misc = loops
            if misc and one_family:
                top.remove(misc[0])
                top.insert(0, misc[0])
            if one_family:
                return top[0], top[1:6], 'medium: instrument from the pack name'
            return top[0], top[1:6], 'REVIEW: only the pack name matched'
        if len(top) == 1:
            if scores[top[0]][2] and fw & self.matcher.keywords[top[0]]:
                return top[0], [], 'high'
            return top[0], [], 'medium: decided by folder names or shared words'
        cats = {self.rows[c]['Category'] for c in top}
        lead_cat = self.rows[top[0]]['Category']
        if len(cats) > 1 and scores[top[0]][3] > max(scores[c][3] for c in top if self.rows[c]['Category'] != lead_cat):
            top = [c for c in top if self.rows[c]['Category'] == lead_cat] + \
                  [c for c in top if self.rows[c]['Category'] != lead_cat]
            cats = {lead_cat}
        if len(cats) == 1 or all(self.rows[c]['Category'] == lead_cat for c in top[:2]):
            misc = [c for c in top if c.endswith('Misc')]
            if misc and scores[top[0]][1] == scores[misc[0]][1]:
                top.remove(misc[0])
                top.insert(0, misc[0])
            return top[0], top[1:6], 'medium: family clear, type unclear'
        if is_loop and set(top[:2]) <= LOOP_TYPES:
            return top[0], top[1:6], 'medium: loop, drums or percussion'
        custom = [c for c in top if self.rows[c]['_custom']]
        if len(custom) == 1 and top[0] == custom[0]:
            return top[0], top[1:6], 'medium: official UCS also fits'
        if scores[top[0]][1] < scores[top[1]][1]:
            return top[0], top[1:6], 'medium: first type word in the name decided'
        return top[0], top[1:6], 'REVIEW: tie'

    def noun(self, catid):
        r = self.rows[catid]
        if catid in NOUN:
            return NOUN[catid]
        cat, sub = r['Category'], r['SubCategory'].lower()
        if cat == 'AI GENERATED':
            return f'AI-generated {sub}' if sub != 'misc' else 'AI-generated sound'
        if sub == 'misc':
            return f"{CAT_NOUN.get(cat, cat.lower())} sound"
        if not r['_custom']:
            return f"{sub} ({cat.lower()})"
        noun = CAT_NOUN.get(cat, '')
        if not noun or noun in sub:
            return sub
        return f"{noun} {sub}" if cat in CAT_FIRST else f"{sub} {noun}"

    # ------------------------------------------------------------------ first pass
    def split(self, path):
        rel = os.path.relpath(path, self.root) if self.root else path
        parts = rel.replace('\\', '/').split('/')
        stem, ext = os.path.splitext(parts[-1])
        return stem, ext, parts[:-1]

    def prepare(self, paths, root):
        """First pass over the whole library: how many files each word occurs in (to keep keywords
        specific) and in how many publishers' folders (a word three or more publishers use is a
        real word; one only a single publisher uses is usually a pack code or a producer name)."""
        self.root = root
        packs = collections.defaultdict(set)
        self.doc = collections.Counter()
        for p in paths:
            stem, _, dirs = self.split(p)
            pack_id = dirs[0] if dirs else ''
            words = set(tokens(stem)) | {w for d in dirs[self.pack_depth:] for w in tokens(d)} | \
                {w for d in dirs[:self.pack_depth][-1:] for w in tokens(d)}
            for w in words:
                self.doc[w] += 1
                if len(packs[w]) < 5:
                    packs[w].add(pack_id)
        self.n = max(1, len(paths))
        self.spread = {w: len(s) for w, s in packs.items()}
        self.vocab = set(self.index) | set(ABBREV) | set(TOOLS)
        # keyword vocabulary for music: the music catalog's own words and describing words, no
        # abbreviations ("Sfx", "Syn") and nothing about the file rather than the sound
        self.kw_vocab = (self.music_words | DESCRIPTORS | SOUND_WORDS) - set(ABBREV) - set(ALIASES) - KEYWORD_NOISE

    def real(self, w):
        if w in self.vocab or w in self.english or w in self.kw_vocab or w in self.genre_tokens:
            return True  # "Dutch" (house), "Dorian", "Jupiter" are names in the dictionary but music words here
        return w not in self.names_list and self.spread.get(w, 0) >= 5

    def common(self, w):
        return self.doc.get(w, 0) / self.n > COMMON_SHARE

    # ------------------------------------------------------------------ one file
    def words(self, stem):
        """Original-case words of a file name: camelCase split, hyphenated codes split, letter+digit
        codes split. Returns [(word, came_from_a_code)]."""
        spaced = re.sub(r'([a-z])([A-Z])', r'\1 \2', stem)
        out = []
        for w in re.split(r'[\s_.()\[\]{},+&!@$%=~;:\'"]+', spaced):
            if not w or set(w) <= set('-#'):
                continue
            if re.match(r'^\d+-\d+$', w):
                out += [(p, True) for p in w.split('-')]  # a bar range ("147-149"), not an index
            elif '-' in w and not KEY_RE.match(w) and w.lower() not in self.index:
                out += self._word_parts([p for p in w.split('-') if p])  # "Crash5-44S": each part
            else:
                out += self._word_parts([w])
        return out

    def _word_parts(self, parts):
        out = []
        for w in parts:
            m = re.match(r'^([A-Za-z]{2,})(\d{1,4})$', w)
            if m and w.lower() not in self.index and w not in MACHINES:
                known = m.group(1).lower() in self.vocab or self.real(m.group(1).lower())
                if m.group(1).isupper() and len(m.group(1)) <= 3:
                    known = False  # "TR66", "DL7": a model or pack code, not an index
                out += [(m.group(1), False), (m.group(2), m.group(1).lower() if known else True)]
                continue
            out.append((w, False))
        return out

    def suggest(self, path):
        stem, ext, dirs = self.split(path)
        self.derived = set()
        self.short_alias = set()
        pack_dirs, inner_dirs = dirs[:self.pack_depth], dirs[self.pack_depth:]
        pack = pack_dirs[-1] if pack_dirs else ''
        pub_words = {w for d in pack_dirs for w in tokens(d)}
        publisher_only = {w for d in pack_dirs[:-1] for w in tokens(d)} - set(tokens(pack_dirs[-1] if pack_dirs else ''))
        orig = self.words(stem)
        orig_words = [w for w, _ in orig]
        # "Drum Loop 7 (No Kick)", "NoKick": the kick is what the loop leaves out
        negated = {orig_words[i + 1].lower() for i, w in enumerate(orig_words[:-1]) if w.lower() in ('no', 'without')}
        negated |= {NEGATED_RE.match(w.lower()).group(1) for w in orig_words if NEGATED_RE.match(w.lower())}
        negated |= {w.rstrip('s') for w in negated}
        # pack codes: "ZEN" (Zenhiser), "FIN" (Finesse), "RawCut" (Rawcutz), "TT" (Techno Tomorrow)
        pack_titles = [w for w in pub_words if w.isalpha() and len(w) >= 3]
        initials = ''.join(w[0] for d in pack_dirs for w in re.findall(r'[A-Za-z]+', d)).lower()
        dir_initials = {i for d in inner_dirs for i in initials_of(d) if len(i) >= 3}  # "FEE" = Festival EDM Essentials
        # "AS-SAP" = Authentic Soundware, Space Age Pop; "ABS" = AudeoBox Swamped; "AHH" = Adventures in Hip Hop
        dir_initials |= {i for d in pack_dirs for i in initials_of(d) if len(i) >= 2}
        dir_initials |= {a + b for a in initials_of(pack_dirs[0]) for b in initials_of(pack_dirs[-1])} if pack_dirs else set()
        is_code = lambda w: len(w) >= 2 and (len(w) >= 3 and any(t.startswith(w) for t in pack_titles) or w == initials or
                                            len(w) <= 4 and initials.startswith(w) or w in dir_initials)
        not_code = lambda ws: [w for w in ws if w in self.index or not is_code(w)]  # "RawCut12" is not raw + cut
        # the kit's name repeated in its files ("Tuff Vibes/Tuff Vibes Clap.wav"): a name, not a sound
        # the kit's name repeated at the start of its files ("Tuff Vibes/Tuff Vibes Clap.wav",
        # "Crumbs Kit/Crumbs Clapz.wav"): a name, not a sound
        parent = [w for w in re.findall(r'[a-z]+', re.sub(r'([a-z])([A-Z])', r'\1 \2', inner_dirs[-1]).lower())
                  if w not in ('kit', 'kits')] if inner_dirs else []
        stem_alpha = re.findall(r'[a-z]+', re.sub(r'([a-z])([A-Z])', r'\1 \2', stem).lower())
        kit_words = set()
        if parent and stem_alpha[:len(parent)] == parent and len(stem_alpha) > len(parent) and \
                not set(parent) & (self.instrument_words | LOOP_WORDS | SHOT_WORDS | STEM_WORDS | GENERIC):
            kit_words = set(parent)
        not_code_raw = not_code
        not_code = lambda ws: [w for w in not_code_raw(ws) if w not in kit_words]
        # the publisher's name where it is spelled out ("Overdrive Audio - Guitars - Shot 16"), but
        # not its words on their own ("Bass Boutique/.../Hero - A - Bass 2" is a bass)
        publisher = [w for d in pack_dirs[:-1] for w in re.findall(r'[a-z0-9]+', d.lower())]
        drop_pub = lambda ws: drop_sequence(ws, publisher)
        file_words = self.expand(self.drop_genre_phrases(drop_pub(not_code(
            [w for w in tokens(stem) if w not in negated and w.rstrip('s') not in negated
             and not NEGATED_RE.match(w)]))))
        dir_words = self.expand([w for d in inner_dirs for w in self.drop_genre_phrases(drop_pub(tokens(d)))])
        pack_words = self.drop_genre_phrases(tokens(pack))
        genre_words = [tokens(pack), [w for d in inner_dirs for w in tokens(d)], tokens(stem)]
        all_words = set(file_words) | set(dir_words)

        # musical facts
        key, key_full, key_words = parse_key(orig_words)
        bars = next((m.group(1) for w in orig_words for m in [BARS_RE.match(w)] if m), '')
        explicit_bpm = BPM_RE.search(stem)
        shot_words = SHOT_WORDS
        # the nearest name that says loop or one-shot decides: the file, then its folders, then the pack
        # ("Drums Hits/Loops/Drum_Loop_2" is a loop, "Hit Kit V3/HK Perc Loops/PL Drum 000 to 119 BPM" too)
        one_shot = loop_said = False
        levels = [file_words] + [self.expand(tokens(d)) for d in reversed(inner_dirs)] + [pack_words]
        for n, level in enumerate(levels):
            level = set(level) | {ALIASES.get(w, w) for w in level}
            if n == len(levels) - 1 or 0 < n and tokens(inner_dirs[-n]) == tokens(pack):
                level -= shot_words  # "Pop Radio Hits", "Hit Kit": chart hits, not one-shots
            if shot_words & level or LOOP_WORDS & level:
                one_shot = bool(shot_words & level) and not LOOP_WORDS & level
                loop_said = not one_shot
                break
        # a tempo in a folder name ("Kit 01 124 BPM Bmin", "Drum Loops/120bpm", "Synth Loops/125")
        dir_bpm = ''
        for d in reversed(inner_dirs):
            found = [m.group(1) or m.group(2) for m in BPM_RE.finditer(d)] + re.findall(r'^\s*(\d{2,3})\s*$', d)
            found = [x for x in found if 60 <= float(x) <= 200]
            if found:
                dir_bpm = found[0]
                break
        kit = bool(STEM_WORDS & set(dir_words))
        # leading all-caps codes that a folder name repeats ("US CH Chords Strings/US_CH_Chord_...")
        lead_codes = set()
        for w, _ in orig:
            if not (w.isupper() and w.isalpha() and len(w) <= 4):
                break
            lead_codes.add(w.lower())
        lead_codes -= ACRONYMS | {'vox'}
        if not any(lead_codes <= {t.lower() for t in re.findall(r'(?<![A-Za-z])[A-Z]{1,4}(?![A-Za-z])', d)}
                   for d in inner_dirs):
            lead_codes = set()
        dir_key = ('', '', set())
        for d in reversed(inner_dirs):
            dir_key = parse_key([w for w, _ in self.words(d)])
            if dir_key[0]:
                break
        root_note = ''
        if one_shot and not {'loop', 'loops'} & set(file_words) and not explicit_bpm and len(key_words) == 1:
            single = next(iter(key_words))
            if len(single) <= 2 and not key.endswith('min'):
                root_note, key, key_full = key.replace('min', ''), '', ''  # "Kick 15 - E": a pitch, not a key
        is_loop = bool(LOOP_WORDS & all_words) or loop_said or bool(explicit_bpm) or bool(bars) or bool(
            key and not one_shot and not any(ROOT_RE.match(w) for w in orig_words)) or bool(dir_bpm and not one_shot)
        if kit and (dir_key[0] or dir_bpm) and not one_shot:
            is_loop = True  # a part of a construction kit ("Kit 02 Am/kit 02 - pluck")
        if is_loop and not key and dir_key[0]:
            key, key_full = dir_key[0], dir_key[1]
        if not is_loop and not root_note:
            root_note = next((w for w in orig_words if ROOT_RE.match(w)), '')
        bpm = parse_bpm(stem, file_words, is_loop or bool(key))
        if bpm and not 40 <= float(bpm) <= 250:
            bpm = ''
        tempos = {x for x in (bpm, dir_bpm) if x}
        if is_loop and not bpm:
            bpm = dir_bpm

        ucs = self.already_ucs(stem + ext)
        if ucs:
            catid, alts, how = ucs, [], 'already UCS'
        else:
            codes = {w for w in file_words if w not in self.index and is_code(w) or w == initials
                     or len(w) <= 4 and initials.startswith(w) or w in dir_initials}
            if len(lead_codes) >= 2:
                codes |= lead_codes
            catid, alts, how = self.choose(file_words, dir_words, pack_words, is_loop, dirs,
                                           publisher_only if len(publisher) == 1 else (), tonal=bool(key),
                                           codes=codes, one_shot=one_shot)
        row = self.rows.get(catid)
        role = self.matcher.keywords.get(catid, set())
        if catid in ONE_SHOT_TYPES and not LOOP_WORDS & all_words and not (kit and dir_bpm) and (
                one_shot or not explicit_bpm):
            is_loop, bpm = False, ''  # a clap with the pack tempo in its name is still a one-shot
        if is_loop and catid and catid.endswith('Misc') and row and row['Category'] in FAMILY_LOOP:
            catid = FAMILY_LOOP[row['Category']]  # "Heavy Perc" with a tempo: a percussion loop
            row = self.rows[catid]
            role = self.matcher.keywords.get(catid, set())
        if catid in LOOP_TYPES:
            is_loop = True
        # the pack and its folders name the genre more reliably than a file ("Q_Rock_Levites_Kick" in Trap Island)
        genre, subgenre = find_genre(genre_words, self.genres)
        music = bool(row and row['_custom'] and (row['Category'] != 'AI GENERATED' or catid == 'AIMusc'))
        if not music:
            genre = subgenre = ''
        tools = [TOOLS[w] for w in dict.fromkeys(file_words + dir_words + pack_words) if w in TOOLS]
        vocal_dir = bool(VOCAL_CONTEXT & set(dir_words))

        # FX Name: [character] [instrument/role] [Loop] [number]
        skip = NOISE | key_words | AI_MARKERS | {'maj', 'min', 'major', 'minor', 'loop', 'loops'}
        if bpm:
            skip.add(bpm.lower())
        if root_note:
            skip.add(root_note.lower())
        kept, numbers, first_type = [], [], None
        # pack volume numbers ("Lead Vocals (Vol. 1)" -> the 1 in "LEADVOX1" is not an index)
        volumes = {int(n) for n in re.findall(r'(?:vol(?:ume)?\.?\s*)(\d+)', ' '.join(dirs), re.I)}
        volumes |= {int(n) for n in re.findall(r'(\d+)\s*$', pack)}
        for i, (w, code) in enumerate(orig):
            lw = w.lower()
            if lw.isdigit() and lw not in MACHINES:
                prev = orig[i - 1][0].lower() if i else ''
                if isinstance(code, str):  # glued: "Kick01", "SYNTH104" count, "Tune3", "Att9" don't
                    code = not (code in role or code in ABBREV or code in CORE_NOUNS) or int(lw) in volumes
                if not code and lw not in tempos and lw != bpm and lw != bars and len(lw) <= 3 and \
                        prev not in ('var', 'variation', 'rr', 'take', 'v', 'version', 'alt', 'pt', 'part', 'vol'):
                    numbers.append((i, lw))
                continue
            if ALIASES.get(lw) in ('loop', 'loops'):
                continue  # "LPS", "LP": the Loop goes at the end
            if lw in skip or 'bpm' in lw or BARS_RE.match(w) or not re.match(r"^[a-z0-9\-']+$", lw):
                continue
            if CHORD_RE.match(w) and not lw.isdigit():
                kept.append((w[:1].upper() + w[1:].lower(), False))  # chord quality: "Maj7", "Sus4"
                continue
            if len(lw) <= 2 and lw not in ABBREV and lw not in SHORT_OK and lw not in FX_SPELL:
                continue  # round-robin, variation and pack codes ("RR", "a", "SP")
            if lw.endswith('s') and len(lw) > 3 and lw not in KEEP_PLURAL and (
                    lw[:-1] in role or lw not in self.index and lw[:-1] in self.index):
                lw = lw[:-1]
                w = w[:-1]  # "Bassdrums" -> Bassdrum, "Claps" -> Clap
            if lw.endswith('loop') and len(lw) > 6:
                lw, w = lw[:-4], w[:-4]  # "Drumloop" -> Drum (Loop goes at the end)
            elif lw.endswith(('lp', 'lps')) and lw.rstrip('s')[:-2] in self.index:
                lw = lw.rstrip('s')[:-2]
                w = w[:len(lw)]  # "Drumlp", "Basslp" -> Drum, Bass
            is_type = (lw in role or lw in ABBREV or ALIASES.get(lw) in role or lw in ('music', 'melody')) \
                and lw not in VARIANT_WORDS
            if lw in publisher_only or lw in negated or (lw in kit_words and not is_type):
                continue  # "Overdrive" (Overdrive Audio), "Kick" in "No Kick"
            if not is_type and w.isupper() and len(w) <= 5 and lw not in ABBREV and (
                    lw not in self.index and lw not in self.english):
                continue  # all-caps pack code ("VEC", "OPS", "MDH")
            if lw in lead_codes and (len(lead_codes) >= 2 or not is_type):
                continue
            if is_code(lw) and (not is_type or len(lw) <= 3 and lw in ABBREV):
                continue  # the pack's or publisher's name or a code of it ("FIN", "Castles", "RawCut", "SD")
            nxt = orig[i + 1] if i + 1 < len(orig) else ('', False)
            if not is_type and len(lw) <= 4 and nxt[1] is not False and nxt[0].isdigit():
                continue  # a parameter label glued to a number ("Acc1", "Tune3", "Att9", "Mic3")
            if lw in ('track', 'song') and nxt[0].isdigit():
                continue  # "Track 02": a song number in a kit
            if lw in ('var', 'vari', 'variation', 'alt', 'ver'):
                continue
            if not is_type and not re.search('[aeiouy]', lw) and lw not in FX_SPELL:
                continue  # no vowel: a code ("DGS", "TT")
            if not is_type and lw not in FX_SPELL and (lw in pub_words or not self.real(lw)):
                parts = [] if lw in pub_words else self.compound(lw)
                if not any(part in role or part in ABBREV or part in CORE_NOUNS for part in parts):
                    parts = []  # "Playboy" is not Play + Boy; only joined instrument words are split
                for part in parts:  # "SYNTHLOOP" -> Synth (+ Loop at the end)
                    if part not in skip and part not in GENERIC and part not in pub_words:
                        kept.append((ABBREV.get(part) or part.title(), part in role or part in ABBREV))
                        if first_type is None and part in role:
                            first_type = i
                continue  # publisher, pack code or kit name
            if NEGATED_RE.match(lw):
                continue  # "NoKick": said by what the loop is, not a word of the name
            word = FX_SPELL.get(lw) or ABBREV.get(lw) or (w.upper() if lw in ACRONYMS else w[:1].upper() + w[1:].lower())
            if is_type and first_type is None:
                first_type = i
            kept.append((word, is_type))
        if row and not any(t for _, t in kept) and not (catid == 'SMPLLoop' and kept):
            sub = row['SubCategory']
            if sub == 'MISC':
                sub = FAMILY_TITLE.get(row['Category'], row['Category'].title())
            sub_title = sub if sub in FAMILY_TITLE.values() else \
                ' '.join(x for x in sub.title().split() if x not in ('Loop', '&')) or FAMILY_TITLE.get(row['Category'], '')
            if sub_title:
                kept.append((sub_title, True))
        kept = [k for k in kept if not k[1]] + [k for k in kept if k[1]]  # "Kick Punchy" -> "Punchy Kick"
        seen, uniq = set(), []
        for k in kept:
            if k[0].lower() not in seen:
                seen.add(k[0].lower())
                uniq.append(k)
        kept = uniq
        # "Hit" and "Shot" follow the instrument: "Bass Hit", not "Hit Bass"
        kept = [k for k in kept if k[0] not in ('Hit', 'Shot')] + [k for k in kept if k[0] in ('Hit', 'Shot')]
        if row and row['Category'] in FAMILY_NOUN:
            noun, has = FAMILY_NOUN[row['Category']]
            if not {k[0].lower() for k in kept} & has:
                last = max((n for n, k in enumerate(kept) if k[1]), default=len(kept) - 1)
                kept.insert(last + 1, (noun, True))  # "Sub" -> "Sub Bass", "Acoustic" -> "Acoustic Guitar"
        if len(numbers) > 1:  # a 3-digit number between 60 and 200 next to others is a tempo
            numbers = [(i, n) for i, n in numbers if not (len(n) == 3 and 60 <= int(n) <= 200)] or numbers
        if len(numbers) == 1 and len(numbers[0][1]) == 3 and 60 <= int(numbers[0][1]) <= 200 and \
                int(numbers[0][1]) % 5 == 0 and (music or vocal_dir):
            numbers = []  # "RIDE_OR_DIE_LEAD_200_DRY": a round tempo, not an index
        if len(numbers) > 1 and any(len(n) <= 2 or n.startswith('0') for _, n in numbers):
            # "Note_21_468": the 3-digit number is a catalogue code, the short one the index
            numbers = [(i, n) for i, n in numbers if len(n) <= 2 or n.startswith('0')]
        after = [n for i, n in numbers if first_type is not None and i > first_type]
        index = int(after[0]) if after else int(numbers[-1][1]) if numbers else 0
        tail = ['Loop'] if is_loop else []
        short = list(kept)

        def length(idx):
            return len(' '.join([w for w, _ in short] + tail + [f'{idx:02d}']))
        for drop in ([k for k in short if k[0].lower() in FILLER],
                     [k for k in short[1:] if not k[1]][::-1],
                     [k for k in short if not k[1]][::-1],
                     [k for k in short if k[1]][1:][::-1]):
            for k in drop:
                if length(max(index, 1)) <= 25 or len(short) <= 1:
                    break
                if k in short:
                    short.remove(k)
        base = ' '.join([w for w, _ in short] + tail) or 'Sound'
        source = source_id(pack)
        user_data = ' '.join(x for x in (f'{bpm}bpm' if bpm else '', key.replace('#', 'sharp'),
                                         root_note.replace('#', 'sharp')) if x)

        def build(idx):
            fx = f'{base} {idx:02d}'
            name = '_'.join(x for x in (catid or 'CATID', fx, self.creator, source, user_data) if x) + ext
            return fx, name
        if index == 0:
            index = 1
        fx_name, new_name = build(index)
        while new_name.lower() in self.names or len(fx_name) > 25:  # unique, and 25 characters at most
            if len(fx_name) > 25 and ' ' in base:
                base = base.split(' ', 1)[1]
            elif new_name.lower() in self.names:
                index += 1
            else:
                break
            fx_name, new_name = build(index)
        self.names.add(new_name.lower())

        # Description: what, how, musical facts, tool
        words = [w for w, _ in kept]
        what = ' '.join(DESC_WORDS.get(w) or (w if w.lower() in ACRONYMS or w in ABBREV.values() and w.isupper()
                                              else w.lower()) for w in words)
        if not row:
            what = what or 'sound'
        elif not (role | self.sub_words.get(catid, set())) & {
                y for w in words for x in w.lower().split() for y in (x, ALIASES.get(x))}:
            what = (what + ' ' + self.noun(catid)).strip()
        what = what.replace(' & ', ' and ').strip()
        if is_loop:
            what = what if what.endswith(' loop') else what + ' loop'
        elif music and row['Category'] not in ('TRACKS', 'STEM') and catid != 'AIMusc':
            what += ' one-shot'
        left_out = sorted({w.rstrip('s') for w in negated if w.rstrip('s') in
                           ('kick', 'snare', 'hat', 'clap', 'bass', 'drum', 'vocal', 'vox', 'perc', 'sub', 'cymbal', 'top')})
        if left_out:
            what += ' without ' + ' and '.join(left_out)  # "Drum loop without kick."
        facts = [f'{bars} bars' if bars else '', f'{bpm} BPM' if bpm else '', key_full,
                 f'root note {root_note}' if root_note else '']
        facts = ', '.join(f for f in facts if f)
        what = what.strip()
        description = what[:1].upper() + what[1:] + '.'
        if facts:
            description += ' ' + facts[:1].upper() + facts[1:] + '.'
        if tools:
            description += f" Generated with {' and '.join(tools)}."

        # Keywords: words of this file, its folders and its pack that say something the name and
        # description don't, are real words, and are not so common that they'd match everything
        taken = {w.lower() for w in re.findall(r"[A-Za-z0-9#&'-]+", fx_name + ' ' + description)}
        taken |= {w.rstrip('s') for w in taken} | {w + 's' for w in taken}
        fam = self.shared_by_cat.get(row['Category'], set()) if row else set()
        genre_text = {w.lower() for w in re.split(r'[^A-Za-z0-9&]+', genre + ' ' + subgenre) if w}
        blocked = (taken | NOISE | set(tokens(genre + ' ' + subgenre)) | genre_text | pub_words - set(pack_words) | role | fam
                   | AI_MARKERS | TRACK_WORDS | STEM_WORDS | GENERIC | key_words | FILLER
                   | {'maj', 'min', 'major', 'minor', 'sharp', 'flat', 'wet', 'dry'} | self.genre_tokens)

        def usable(w):
            return (w.isalpha() and len(w) >= 3 and w not in blocked and w not in KEYWORD_NOISE
                    and 'loop' not in w and not self.common(w)
                    and not KEY_RE.match(w) and not ROOT_RE.match(w.upper()))

        def spell(w):
            if w.endswith('s') and w[:-1] in self.kw_vocab and w not in KEEP_PLURAL:
                w = w[:-1]  # "Phrases" -> Phrase
            return None if w in blocked else w.title()
        # original words only: parts of a split name ("Ghosthack" -> Ghost, Hack; "Template" ->
        # Temp, Late) are not keywords; neither are pack codes ("ZEN", "SIM") or song/kit titles
        source_words = [w for w in tokens(stem) + [w for d in inner_dirs for w in tokens(d)]]
        instruments = CORE_NOUNS | {x for ws in FAMILY_DIR.values() for x in ws}
        candidates = [w for w in dict.fromkeys(source_words) if usable(w) and not is_code(w)
                      and (w in self.kw_vocab or row and not row['_custom'] and w in self.vocab)
                      and w not in instruments and w not in kit_words]  # "Keys" from "Keys & Strings" on a viola misleads
        candidates += [w for w in pack_words if usable(w) and w in DESCRIPTORS]
        out = []
        for w in candidates:
            spelled = spell(w)
            if spelled and spelled.lower().rstrip('s') not in {o.lower().rstrip('s') for o in out}:
                out.append(spelled)
        out = out[:8]
        if not how.startswith('REVIEW'):
            # the plain names people search for ("Bass Drum" for a kick), unless already said
            fx_low = {w.lower() for w in fx_name.split()}
            for syn in SYNONYMS.get(catid, ()):
                parts = syn.lower().split()
                if not set(parts) & fx_low and syn.lower() not in description.lower() and \
                        not set(parts) & genre_text and syn.lower().replace(' ', '') not in genre_text and \
                        syn.lower() not in {o.lower() for o in out}:
                    out.append(syn)
        keywords = ', '.join(dict.fromkeys(out + tools))

        return {
            'Path': path, 'Pack': ' / '.join(pack_dirs), 'Confidence': how, 'CatID': catid or '',
            'Category': row['Category'] if row else '', 'SubCategory': row['SubCategory'] if row else '',
            'FX Name': fx_name, 'Suggested File Name': new_name, 'Description': description,
            'Genre': genre, 'Subgenre': subgenre, 'BPM': bpm, 'Key': key, 'Root Note': root_note,
            'Bars': bars, 'Keywords': keywords, 'Alternatives': ', '.join(alts),
        }


COLUMNS = ['Path', 'Pack', 'Confidence', 'CatID', 'Category', 'SubCategory', 'FX Name', 'Suggested File Name',
           'Description', 'Genre', 'Subgenre', 'BPM', 'Key', 'Root Note', 'Bars', 'Keywords', 'Alternatives']


def collect(source):
    if os.path.isdir(source):
        for dirpath, dirnames, filenames in os.walk(source):
            dirnames[:] = sorted(d for d in dirnames if not d.startswith('.') and d != '__MACOSX')
            for f in sorted(filenames):
                yield os.path.join(dirpath, f)
    else:
        with open(source, encoding='utf-8', errors='replace') as f:
            for line in f:
                if line.strip():
                    yield line.rstrip('\r\n')


VALID_KEYS = set(MAJOR.values()) | set(MINOR.values())


def problems(r, genre_pairs):
    """Rule checks from docs/METADATA-STYLE-GUIDE.md. Returns a list of problems (empty = OK)."""
    out = []
    fx, name, desc = r['FX Name'], r['Suggested File Name'], r['Description']
    if len(fx) > 25:
        out.append('FX Name longer than 25 characters')
    if not re.match(r"^[A-Za-z0-9][A-Za-z0-9 '\-]* \d{2,}$", fx) or '  ' in fx:
        out.append('FX Name format')
    if any(w[:1].isalpha() and not w[:1].isupper() for w in fx.split()):
        out.append('FX Name not Title Case')
    stem = os.path.splitext(name)[0]
    if not name.isascii() or re.search(r'[/\\#&?*:|"<>()\[\]]', stem):
        out.append('file name has characters that are not allowed')
    fields = stem.split('_')
    if not 4 <= len(fields) <= 5 or any(not f.strip() or f != f.strip() for f in fields):
        out.append('file name fields')
    if r['CatID'] and fields[0] != r['CatID']:
        out.append('file name does not start with the CatID')
    if not desc.endswith('.') or not (desc[:1].isupper() or desc[:1].isdigit()) or '  ' in desc or '..' in desc \
            or desc.startswith(' '):
        out.append('Description format')
    if r['Key'] and r['Key'] not in VALID_KEYS:
        out.append('Key spelling')
    if r['BPM'] and not 40 <= float(r['BPM']) <= 250:
        out.append('BPM out of range')
    if r['Root Note'] and not ROOT_OK.match(r['Root Note']):
        out.append('Root Note format')
    if r['Subgenre'] and (r['Genre'], r['Subgenre']) not in genre_pairs:
        out.append('Subgenre not in the genre list')
    if r['Genre'] and r['Genre'] not in {g for g, _ in genre_pairs}:
        out.append('Genre not in the genre list')
    kws = [k.strip() for k in r['Keywords'].split(',') if k.strip()]
    lower = [k.lower() for k in kws]
    if len(set(lower)) != len(lower):
        out.append('duplicate keyword')
    if len(kws) > 12:
        out.append('more than 12 keywords')
    fx_words = {w.lower() for w in fx.split()}
    if any(set(k.split()) & fx_words for k in lower):
        out.append('keyword repeats FX Name')
    genre_words = {w.lower() for w in (r['Genre'] + ' ' + r['Subgenre']).split()}
    if any(k in genre_words for k in lower):
        out.append('genre in keywords')
    if any(not re.match(r'^[A-Z][A-Za-z]*( [A-Z][A-Za-z]*)?$', k) and k not in TOOLS.values() for k in kws):
        out.append('keyword format')
    return out


def write(rows, out):
    """Write rows (an iterator) as they come, so even a library of 700 000 files fits in memory.
    Returns (output path, Counter of confidence labels, Counter of CatIDs)."""
    confidence, catids = collections.Counter(), collections.Counter()
    issues = collections.Counter()
    genre_pairs = {(g['Genre'], g['Subgenre']) for g in build_catalog.load_genres()}
    issue_file = open(os.path.splitext(out)[0] + '-problems.csv', 'w', encoding='utf-8', newline='')
    issue_writer = csv.writer(issue_file)
    issue_writer.writerow(['Path', 'Problem', 'FX Name', 'Suggested File Name', 'Keywords'])

    def counted(rows):
        for r in rows:
            confidence[r['Confidence'].split(':')[0]] += 1
            catids[r['CatID'] or '(none)'] += 1
            for problem in problems(r, genre_pairs):
                issues[problem] += 1
                issue_writer.writerow([r['Path'], problem, r['FX Name'], r['Suggested File Name'], r['Keywords']])
            yield r
    write.issues = issues

    if out.lower().endswith('.xlsx'):
        try:
            import openpyxl
            from openpyxl.formatting.rule import FormulaRule
            from openpyxl.styles import Font, PatternFill
        except ImportError:
            out = out[:-5] + '.csv'
            print('openpyxl not installed, writing CSV instead')
        else:
            wb = openpyxl.Workbook(write_only=True)
            ws = wb.create_sheet('Suggestions')
            widths = [60, 24, 26, 12, 16, 16, 26, 60, 60, 18, 18, 7, 8, 9, 6, 50, 40]
            for i, w in enumerate(widths):
                ws.column_dimensions[openpyxl.utils.get_column_letter(i + 1)].width = w
            ws.freeze_panes = 'B2'
            header = []
            for c in COLUMNS:
                cell = openpyxl.cell.WriteOnlyCell(ws, value=c)
                cell.font = Font(bold=True)
                header.append(cell)
            ws.append(header)
            n = 1
            for r in counted(rows):
                ws.append([r[c] for c in COLUMNS])
                n += 1
            last = openpyxl.utils.get_column_letter(len(COLUMNS))
            ws.auto_filter.ref = f'A1:{last}{n}'
            ws.conditional_formatting.add(f'A2:{last}{n}', FormulaRule(
                formula=['LEFT($C2,6)="REVIEW"'], fill=PatternFill('solid', fgColor='FFF2CC', bgColor='FFF2CC')))
            summary = wb.create_sheet('Summary')
            summary.append(['Files', n - 1])
            for label, k in confidence.most_common():
                summary.append([f'Confidence: {label}', k])
            summary.append([])
            summary.append(['CatID', 'Files'])
            for catid, k in catids.most_common():
                summary.append([catid, k])
            wb.save(out)
            issue_file.close()
            return out, confidence, catids
    with open(out, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, COLUMNS)
        w.writeheader()
        for r in counted(rows):
            w.writerow(r)
    issue_file.close()
    return out, confidence, catids


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('source', help='folder to scan, or a text file with one path per line')
    parser.add_argument('-o', '--output', default='metadata-suggestions.xlsx', help='.xlsx or .csv')
    parser.add_argument('--root', help='folder the paths are relative to (default: the scanned folder, or the '
                                       'common folder of all paths in the list)')
    parser.add_argument('--creator', default='CREATOR', help='CreatorID for the suggested file names')
    parser.add_argument('--pack-depth', type=int, default=1,
                        help='folder level that holds the pack name: 1 = Pack/..., 2 = Publisher/Pack/...')
    parser.add_argument('--prefer', choices=['music', 'sfx', 'none'], default='music',
                        help='weigh music categories (sample packs) or official UCS (sound effects) higher')
    args = parser.parse_args()

    paths = [p for p in collect(args.source)
             if os.path.splitext(p)[1].lower() in AUDIO and not os.path.basename(p).startswith(('.', '._'))
             and '/__MACOSX/' not in p.replace('\\', '/')]
    if not paths:
        sys.exit('no audio files found')
    root = args.root or (args.source if os.path.isdir(args.source) else os.path.commonpath(paths))
    if root in paths:
        root = os.path.dirname(root)
    suggester = Suggester(args.creator, args.pack_depth, args.prefer)
    suggester.prepare(paths, root)
    out, confidence, _ = write((suggester.suggest(p) for p in paths), args.output)
    print(f'{len(paths)} files -> {out} ({confidence["REVIEW"]} marked REVIEW)')
    issues = write.issues
    print(f'rule check: {sum(issues.values())} problems' + ''.join(f'\n  {n:7} {p}' for p, n in issues.most_common()))


if __name__ == '__main__':
    main()
