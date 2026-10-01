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
         'bpm', 'key', 'wet', 'dry', 'demo', 'preview', 'vol', 'volume', 'bonus', 'free', 'misc', 'various'}

# Key spelling from the style guide: one name per pitch.
MAJOR = {'C': 'C', 'C#': 'Db', 'DB': 'Db', 'D': 'D', 'D#': 'Eb', 'EB': 'Eb', 'E': 'E', 'F': 'F', 'F#': 'F#',
         'GB': 'F#', 'G': 'G', 'G#': 'Ab', 'AB': 'Ab', 'A': 'A', 'A#': 'Bb', 'BB': 'Bb', 'B': 'B', 'CB': 'B'}
MINOR = {'C': 'Cmin', 'C#': 'C#min', 'DB': 'C#min', 'D': 'Dmin', 'D#': 'Ebmin', 'EB': 'Ebmin', 'E': 'Emin',
         'F': 'Fmin', 'F#': 'F#min', 'GB': 'F#min', 'G': 'Gmin', 'G#': 'G#min', 'AB': 'G#min', 'A': 'Amin',
         'A#': 'Bbmin', 'BB': 'Bbmin', 'B': 'Bmin'}
FULL = {'#': ' sharp', 'b': ' flat'}
KEY_RE = re.compile(r'^([a-g])(#|b|sharp|flat|s)?(m|min|minor|maj|major)?$', re.I)
ROOT_RE = re.compile(r'^([A-G])(#|b)?(-?[0-8])$')
BPM_RE = re.compile(r'(\d{2,3}(?:\.\d)?)\s*bpm', re.I)

CAT_NOUN = {'DRUMS': 'drum', 'PERCUSSION': 'percussion', 'SYNTH': 'synth', 'BASS': 'bass', 'GUITAR': 'guitar',
            'ORCHESTRA': 'orchestra', 'VOCALS': 'vocal', 'SAMPLE': 'sample', 'TRACKS': 'track', 'STEM': 'stem'}
CAT_FIRST = {'SYNTH', 'VOCALS', 'SAMPLE', 'ORCHESTRA'}
NOUN = {'DRMLoop': 'drum loop', 'DRMFill': 'drum fill', 'DRMBreak': 'drum break', 'DRMTop': 'top loop',
        'DRMHat': 'hi-hat', 'DRMRim': 'rimshot', 'DRMSnap': 'finger snap', 'DRMClap': 'clap',
        'PERCLoop': 'percussion loop', 'TRKStinger': 'stinger', 'TRKJingle': 'jingle', 'STEMMix': 'full mix',
        'BASSElec': 'electric bass', 'BASSUpright': 'upright bass', 'KEYSEpiano': 'electric piano',
        'WWNDReed': 'free-reed instrument', 'VOCLLead': 'lead vocal', 'VOCLBacking': 'backing vocal'}


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
        note, acc, qual = m.group(1).upper(), (m.group(2) or ''), (m.group(3) or '').lower()
        acc = {'sharp': '#', 's': '#', 'flat': 'b'}.get(acc.lower(), acc)
        if not qual and nxt in ('major', 'minor', 'maj', 'min'):
            qual = nxt
        # a lone letter (a, b, e...) is only a key when it is uppercase and next to a tempo or quality
        prev = words_orig[i - 1].lower() if i else ''
        tempo_near = nxt.endswith('bpm') or nxt.isdigit() or prev.endswith('bpm') or (prev.isdigit() and len(prev) >= 2)
        if not acc and not qual and not (w.isupper() and len(w) == 1 and tempo_near):
            continue
        if acc == 's' and not qual:
            continue
        name = note + acc.upper().replace('B', 'b') if acc else note
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
        return m.group(1)
    if is_loop:
        for w in words:
            if w.isdigit() and 60 <= int(w) <= 200 and not w.startswith('0'):
                return w
    return ''


def load_genres():
    genres = build_catalog.load_genres()
    lookup = {}
    for g in genres:
        lookup[re.sub(r'[^a-z0-9]', '', g['Subgenre'].lower().replace('&', 'and'))] = (g['Genre'], g['Subgenre'])
    for g in {g['Genre'] for g in genres}:
        lookup.setdefault(re.sub(r'[^a-z0-9]', '', g.lower().replace('&', 'and')), (g, ''))
    lookup.update({'dnb': ('Bass Music', 'Drum & Bass'), 'lofi': ('Hip Hop', 'Lo-Fi Hip Hop'),
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


ABBREV = {'hh': 'Hi-Hat', 'gtr': 'Guitar', 'oh': 'Open Hat', 'ch': 'Closed Hat', 'perc': 'Perc', 'fx': 'FX',
          'sfx': 'SFX', 'vox': 'Vox', 'ep': 'E-Piano', 'bd': 'Kick', 'sd': 'Snare'}
FILLER = {'into', 'the', 'of', 'and', 'with', 'to', 'a', 'an', 'in', 'on'}
TOOLS = {'elevenlabs': 'ElevenLabs', 'suno': 'Suno', 'udio': 'Udio', 'stableaudio': 'Stable Audio',
         'audiogen': 'AudioGen', 'audiocraft': 'AudioCraft', 'audioldm': 'AudioLDM', 'musicgen': 'MusicGen'}
TRACK_WORDS = {'track', 'tracks', 'song', 'songs', 'music', 'bgm', 'soundtrack', 'ost', 'score', 'cue', 'cues',
               'theme', 'themes', 'stinger', 'stingers', 'jingle', 'jingles', 'full', 'instrumental'}
# Role words that describe one variant; as synonyms they would mislead ("Open" on a closed hi-hat).
VARIANT_WORDS = {'open', 'closed', 'pedal', 'clean', 'muted', 'mute', 'soft', 'hard', 'short', 'long', 'white',
                 'pink', 'brown', 'dark', 'bright', 'full', 'double', 'steel', 'felt', 'prepared', 'grand',
                 'upright', 'french', 'tenor', 'alto', 'soprano', 'baritone', 'electric', 'acoustic', 'jazz',
                 'slide', 'classical', 'spanish', 'concert', 'digital', 'synthetic', 'orchestral', 'egg',
                 'brush', 'brushes'}
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
    def __init__(self, creator):
        _, rows = build_catalog.load()
        self.rows = {r['CatID']: r for r in rows}
        self.matcher = build_catalog.Matcher(rows)
        self.genres = load_genres()
        self.creator = creator
        # words used to split joined spellings ("bassdrum" -> Bass Drum): music keywords only
        self.music_words = {w for r in rows if r['_custom'] and r['CatShort'] != 'AI'
                            for w in self.matcher.keywords[r['CatID']] if len(w) >= 3}
        self.official_words = {w for r in rows if not r['_custom'] for w in self.matcher.keywords[r['CatID']]}
        by_cat = collections.defaultdict(list)
        for r in rows:
            by_cat[r['Category']].append(self.matcher.keywords[r['CatID']])
        # family words: in at least half of a category's subcategories
        self.family = {}
        for cat, sets in by_cat.items():
            count = collections.Counter(w for s in sets for w in s)
            self.family[cat] = {w for w, n in count.items() if len(sets) > 1 and n * 2 >= len(sets)}
        self.used = collections.Counter()

    def choose(self, file_words, dir_words):
        """Score = 2 x file-name matches + folder-name matches. Ties: the CatID matching the
        earliest file-name word, then the family's MISC, then music before official UCS."""
        has_ai = bool(AI_MARKERS & (set(file_words) | set(dir_words)))
        fw, dw = set(file_words), set(dir_words)
        position = {}
        for i, w in enumerate(file_words):
            position.setdefault(w, i)
        scores = {}
        for catid, kws in self.matcher.keywords.items():
            if catid.startswith('AI') and not has_ai:
                continue
            if catid.startswith('TRK') and not (TRACK_WORDS & (fw | dw)):
                continue  # genre words alone don't make a file a finished track
            s = 2 * len(fw & kws) + len(dw & kws)
            if s:
                first = min((position[w] for w in fw & kws), default=99)
                scores[catid] = (s, first)
        if not scores:
            return None, [], 'REVIEW: no match'
        best = max(s for s, _ in scores.values())
        top = [c for c, (s, _) in scores.items() if s == best]
        if len(top) == 1:
            file_best = max(len(fw & self.matcher.keywords[c]) for c in scores)
            sure = len(fw & self.matcher.keywords[top[0]]) == file_best
            return top[0], [], 'high' if sure else 'medium: decided by folder names'
        cats = {self.rows[c]['Category'] for c in top}
        misc = [c for c in top if c.endswith('Misc')]

        def rank(c):
            return (scores[c][1], not self.rows[c]['_custom'], c)
        top.sort(key=rank)
        if len(cats) == 1 and misc and scores[top[0]][1] == scores[top[-1]][1]:
            top.remove(misc[0])
            top.insert(0, misc[0])
        custom = [c for c in top if self.rows[c]['_custom']]
        if len(custom) == 1 and top[0] == custom[0]:
            how = 'medium: official UCS also fits'
        elif scores[top[0]][1] < scores[top[1]][1]:
            how = 'medium: first type word in the name decided'
        else:
            how = 'REVIEW: tie'
        return top[0], top[1:6], how

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

    def suggest(self, path, root):
        rel = os.path.relpath(path, root) if root else path
        parts = rel.replace('\\', '/').split('/')
        stem, ext = os.path.splitext(parts[-1])
        dirs = parts[:-1]
        pack = dirs[0] if dirs else ''
        spaced = re.sub(r'([a-z])([A-Z])', r'\1 \2', stem)
        orig_words = [w for w in re.split(r'[\s_.()\[\]{},+]+', spaced) if w]
        file_words = tokens(stem)
        dir_words = [w for d in dirs for w in tokens(d)]

        key, key_full, key_words = parse_key(orig_words)
        bars = next((m.group(1) for w in orig_words for m in [BARS_RE.match(w)] if m), '')
        explicit_bpm = BPM_RE.search(stem)
        is_loop = bool({'loop', 'loops'} & set(file_words + dir_words)) or bool(explicit_bpm) or bool(key and not
                       any(ROOT_RE.match(w) for w in orig_words))
        bpm = parse_bpm(stem, file_words, is_loop or bool(key))
        root_note = '' if is_loop else next((w for w in orig_words if ROOT_RE.match(w)), '')

        ucs, _ = self.matcher.suggest(stem + ext)
        if ucs:
            catid, alts, how = ucs, [], 'already UCS'
        else:
            catid, alts, how = self.choose(file_words, dir_words)
        row = self.rows.get(catid)
        genre, subgenre = find_genre([file_words, dir_words], self.genres)
        music = bool(row and row['_custom'] and (row['Category'] != 'AI GENERATED' or catid == 'AIMusc'))
        if not music:
            genre = subgenre = ''
        tools = [TOOLS[w] for w in dict.fromkeys(file_words + dir_words) if w in TOOLS]

        # FX Name: [character] [instrument/role] [Loop] [number]
        role = self.matcher.keywords.get(catid, set())
        pack_code = {w.lower() for w in orig_words[:1] if w.isupper() and len(w) <= 5 and w.lower() not in role}
        skip = NOISE | pack_code | key_words | {bpm, root_note.lower()} | AI_MARKERS
        kept, index = [], ''
        for w in orig_words:
            lw = w.lower()
            if lw == bpm:
                continue
            if lw.isdigit():
                if len(lw) <= 2 or int(lw) < 60:
                    index = lw
                continue
            if lw in skip or BPM_RE.match(w) or BARS_RE.match(w) or re.match(r'^\d+bpm$', lw):
                continue
            if lw in ('maj', 'min', 'major', 'minor', 'loop', 'loops'):
                continue
            word = ABBREV.get(lw) or (w if w.isupper() and len(w) <= 4 else w[:1].upper() + w[1:].lower())
            kept.append((word, (lw in role or lw in ABBREV) and lw not in VARIANT_WORDS))
        if row and not any(is_type for _, is_type in kept):
            kept.append((row['SubCategory'].title(), True))
        # packs often start with the type ("Kick Punchy"): move that leading run behind the
        # describing words ("Punchy Kick"), as the style guide orders [character] [type]
        lead = 0
        while lead < len(kept) and kept[lead][1]:
            lead += 1
        if 0 < lead < len(kept):
            kept = kept[lead:] + kept[:lead]
        kept = list(dict.fromkeys(kept))
        words = [w for w, _ in kept] + (['Loop'] if is_loop else [])
        if not index:
            self.used[(catid, ' '.join(words))] += 1
            index = str(self.used[(catid, ' '.join(words))])
        index = f"{int(index):02d}"
        # shorten to 25 characters: filler first, then extra describing words, then extra type words
        short = list(kept)
        def length():
            return len(' '.join([w for w, _ in short] + (['Loop'] if is_loop else []) + [index]))
        for drop in ([k for k in short if k[0].lower() in FILLER],
                     [k for k in short[1:] if not k[1]][::-1],
                     [k for k in short if k[1]][1:][::-1]):
            for k in drop:
                if length() <= 25 or len(short) <= 1:
                    break
                short.remove(k)
        base = ' '.join([w for w, _ in short] + (['Loop'] if is_loop else [])) or 'Sound'
        fx_name = f'{base} {index}'

        user_data = ' '.join(x for x in (f'{bpm}bpm' if bpm else '', key.replace('#', 'sharp'),
                                         root_note.replace('#', 'sharp')) if x)
        new_name = '_'.join(x for x in (catid or 'CATID', fx_name, self.creator, source_id(pack), user_data)
                            if x) + ext

        # Description: what, how, musical facts, tool
        what_words = [w.lower() if not (w.isupper() or '-' in w) else w.lower() if '-' in w else w
                      for w in words if w != 'Loop']
        what = ' '.join(what_words)
        if not row:
            what = what or 'sound'
        elif not role & {w.lower() for w in words}:
            what = (what + ' ' + self.noun(catid)).strip()
        if is_loop:
            what += ' loop'
        elif music and row['Category'] not in ('TRACKS', 'STEM') and catid != 'AIMusc':
            what += ' one-shot'
        facts = [f'{bars} bars' if bars else '', f'{bpm} BPM' if bpm else '', key_full,
                 f'root note {root_note}' if root_note else '']
        facts = ', '.join(f for f in facts if f)
        description = what[:1].upper() + what[1:] + '.'
        if facts:
            description += ' ' + facts[:1].upper() + facts[1:] + '.'
        if tools:
            description += f" Generated with {' and '.join(tools)}."

        # Keywords: folder words and synonyms not already used, no genre/tempo/key/pack words
        taken = {w.lower() for w in re.findall(r'[A-Za-z0-9#&-]+', fx_name + ' ' + description)}
        taken |= {w.rstrip('s') for w in taken} | {w + 's' for w in taken}
        blocked = (taken | NOISE | set(tokens(genre + ' ' + subgenre)) | set(tokens(pack)) | pack_code
                   | self.family.get(row['Category'], set()) if row else set()) | AI_MARKERS

        def nice(w):
            return w.isalpha() and len(w) > 3 and w not in blocked and not KEY_RE.match(w)

        def spell(w):
            # joined spellings such as "bassdrum" become "Bass Drum"; variants of another sound are dropped
            for i in range(3, len(w) - 2):
                first, second = w[:i], w[i:]
                if first in self.music_words and second in self.music_words:
                    if {first, second} <= taken or (first in VARIANT_WORDS and first not in file_words + dir_words):
                        return None
                    return f'{first.title()} {second.title()}'
            return w.title()
        kw = [w for w in dir_words + file_words if nice(w) and w not in role]
        if row and row['Category'] not in ('AI GENERATED', 'TRACKS') and not how.startswith('REVIEW'):
            # up to five synonyms, plain English words (also used by official UCS) first
            synonyms = sorted((w for w in role - VARIANT_WORDS if nice(w)),
                              key=lambda w: (w not in self.official_words, w))
            kw += synonyms[:5]
        out = []
        for w in kw:
            spelled = spell(w)
            if spelled and spelled.rstrip('s') not in {o.rstrip('s') for o in out}:
                out.append(spelled)
        keywords = ', '.join(dict.fromkeys(out[:12] + tools))

        return {
            'Path': path, 'Pack': pack, 'Confidence': how, 'CatID': catid or '',
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


def write(rows, out):
    if out.lower().endswith('.xlsx'):
        try:
            import openpyxl
            from openpyxl.styles import Alignment, Font, PatternFill
        except ImportError:
            out = out[:-5] + '.csv'
            print('openpyxl not installed, writing CSV instead')
        else:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = 'Suggestions'
            ws.append(COLUMNS)
            review = PatternFill('solid', fgColor='FFF2CC')
            for r in rows:
                ws.append([r[c] for c in COLUMNS])
                if r['Confidence'].startswith('REVIEW'):
                    for cell in ws[ws.max_row]:
                        cell.fill = review
            for cell in ws[1]:
                cell.font = Font(bold=True)
            widths = [60, 18, 26, 12, 16, 16, 26, 60, 60, 18, 18, 7, 8, 9, 6, 50, 40]
            for i, w in enumerate(widths):
                ws.column_dimensions[openpyxl.utils.get_column_letter(i + 1)].width = w
            for row in ws.iter_rows(min_row=2):
                for cell in row:
                    cell.alignment = Alignment(vertical='top', wrap_text=cell.column in (9, 16))
            ws.freeze_panes = 'B2'
            ws.auto_filter.ref = ws.dimensions
            summary = wb.create_sheet('Summary')
            summary.append(['Files', len(rows)])
            for label, n in collections.Counter(r['Confidence'].split(':')[0] for r in rows).most_common():
                summary.append([f'Confidence: {label}', n])
            summary.append([])
            summary.append(['CatID', 'Files'])
            for catid, n in collections.Counter(r['CatID'] or '(none)' for r in rows).most_common():
                summary.append([catid, n])
            wb.save(out)
            return out
    with open(out, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, COLUMNS)
        w.writeheader()
        w.writerows(rows)
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('source', help='folder to scan, or a text file with one path per line')
    parser.add_argument('-o', '--output', default='metadata-suggestions.xlsx', help='.xlsx or .csv')
    parser.add_argument('--root', help='folder the paths are relative to (default: the scanned folder, or the '
                                       'common folder of all paths in the list)')
    parser.add_argument('--creator', default='CREATOR', help='CreatorID for the suggested file names')
    args = parser.parse_args()

    paths = [p for p in collect(args.source)
             if os.path.splitext(p)[1].lower() in AUDIO and not os.path.basename(p).startswith(('.', '._'))
             and '/__MACOSX/' not in p.replace('\\', '/')]
    if not paths:
        sys.exit('no audio files found')
    root = args.root or (args.source if os.path.isdir(args.source) else os.path.commonpath(paths))
    if root in paths:
        root = os.path.dirname(root)
    suggester = Suggester(args.creator)
    rows = [suggester.suggest(p, root) for p in paths]
    out = write(rows, args.output)
    review = sum(r['Confidence'].startswith('REVIEW') for r in rows)
    print(f'{len(rows)} files -> {out} ({review} marked REVIEW)')


if __name__ == '__main__':
    main()
