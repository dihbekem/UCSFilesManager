"""Build data.txt, keywords/*.txt, UCS(folders).zip and catalog/_categorylist.xlsx
from the category CSVs in catalog/.

    python tools/build_catalog.py            # validate and write everything
    python tools/build_catalog.py --check    # validate only
    python tools/build_catalog.py --match "Kick 808 01.wav" "vocal_chop_Am.wav"
    python tools/build_catalog.py --test     # run catalog/match_tests.csv

Sources:
    catalog/ucs_official.csv       official UCS list (keep in sync with UCS releases)
    catalog/custom_categories.csv  AI GENERATED + music production extension

The CSVs are the source of truth: keywords/*.txt is regenerated from the
"Synonyms - Comma Separated" column, so edit keywords in the CSV, not in the txt files.
"""
import argparse
import csv
import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG_DIR = os.path.join(ROOT, 'catalog')
SOURCES = ['ucs_official.csv', 'custom_categories.csv']
DATA_FILE = os.path.join(ROOT, 'data.txt')
KEYWORDS_DIR = os.path.join(ROOT, 'keywords')
FOLDERS_ZIP = os.path.join(ROOT, 'UCS(folders).zip')
XLSX_FILE = os.path.join(CATALOG_DIR, '_categorylist.xlsx')
SYN = 'Synonyms - Comma Separated'
ZIP_DATE = (2024, 6, 27, 0, 0, 0)


def load():
    rows = []
    header = None
    for name in SOURCES:
        with open(os.path.join(CATALOG_DIR, name), encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            header = header or reader.fieldnames
            for line, row in enumerate(reader, start=2):
                row['_source'] = f'{name}:{line}'
                row['_custom'] = name != 'ucs_official.csv'
                rows.append(row)
    return header, rows


def keywords_of(row):
    return [k.strip() for k in row[SYN].split(',') if k.strip()]


def validate(rows):
    errors, warnings = [], []
    seen = {}
    for row in rows:
        where = row['_source']
        cat, sub, catid, short = row['Category'], row['SubCategory'], row['CatID'], row['CatShort']
        if not (cat and sub and catid and short):
            errors.append(f'{where}: Category, SubCategory, CatID and CatShort are all required')
            continue
        for field, value in (('Category', cat), ('SubCategory', sub), ('CatID', catid)):
            if ',' in value:
                errors.append(f'{where}: {field} "{value}" contains a comma (breaks data.txt)')
        if any(c in catid for c in ' _-'):
            errors.append(f'{where}: CatID "{catid}" must not contain spaces, "_" or "-"')
        if catid in seen:
            errors.append(f'{where}: CatID "{catid}" already used at {seen[catid]}')
        seen[catid] = where
        if row['_custom']:
            if cat != cat.upper() or sub != sub.upper():
                errors.append(f'{where}: Category/SubCategory must be UPPERCASE ("{cat}" / "{sub}")')
            if not catid.startswith(short):
                errors.append(f'{where}: CatID "{catid}" does not start with CatShort "{short}"')
            if not keywords_of(row):
                errors.append(f'{where}: "{catid}" has no keywords, it can never be suggested')
        for k in keywords_of(row):
            # The app splits file names on "_" only, so these keywords can never match.
            if ' ' in k or '_' in k:
                (errors if row['_custom'] else warnings).append(
                    f'{where}: keyword "{k}" in {catid} contains a space/underscore and can never match')
            if k != k.lower() and row['_custom']:
                errors.append(f'{where}: keyword "{k}" in {catid} must be lowercase')
    # Official UCS has a few of these (BEEP/RAIN/WIND) that move_order() works around;
    # don't let the extension add more.
    ids = [r['CatID'] for r in rows]
    for row in rows:
        if row['_custom']:
            for other in ids:
                if other != row['CatID'] and (other.startswith(row['CatID']) or row['CatID'].startswith(other)):
                    errors.append(f"{row['_source']}: CatID \"{row['CatID']}\" and \"{other}\" start the same way, "
                                  'already-UCS files would be moved to the wrong folder')
    pairs = {}
    for row in rows:
        pairs.setdefault((row['Category'], row['SubCategory']), []).append(row['CatID'])
    for (cat, sub), ids in pairs.items():
        if len(ids) > 1:
            errors.append(f'{cat}/{sub} is used by several CatIDs: {", ".join(ids)}')
    return errors, warnings


def move_order(rows):
    """Order rows so that a CatID that is a prefix of another CatID comes after it.

    The app moves already-UCS files with file_name.startswith(CatID), walking
    data.txt top to bottom, so "RAIN" listed before "RAINClth" would swallow
    every RAINClth_* file.
    """
    ids = [r['CatID'] for r in rows]
    depth = {}

    def get_depth(catid):
        if catid not in depth:
            longer = [o for o in ids if o != catid and o.startswith(catid)]
            depth[catid] = 1 + max(map(get_depth, longer)) if longer else 0
        return depth[catid]

    return sorted(rows, key=lambda r: get_depth(r['CatID']))


def write_data(rows):
    with open(DATA_FILE, 'w', encoding='utf-8', newline='') as f:
        for row in move_order(rows):
            f.write(f"{row['Category']},{row['SubCategory']},{row['CatID']}\r\n")


def write_keywords(rows):
    wanted = {row['CatID'] for row in rows}
    for name in os.listdir(KEYWORDS_DIR):
        if name.endswith('.txt') and name[:-4] not in wanted:
            os.remove(os.path.join(KEYWORDS_DIR, name))
            print(f'removed stale keywords/{name}')
    for row in rows:
        with open(os.path.join(KEYWORDS_DIR, row['CatID'] + '.txt'), 'w', encoding='utf-8', newline='') as f:
            f.write(row[SYN].strip())


def write_folders_zip(rows):
    dirs = []
    for row in rows:
        for d in (f"UCS/{row['Category']}/", f"UCS/{row['Category']}/{row['SubCategory']}/"):
            if d not in dirs:
                dirs.append(d)
    with zipfile.ZipFile(FOLDERS_ZIP, 'w') as z:
        for d in dirs:
            info = zipfile.ZipInfo(d, ZIP_DATE)
            info.external_attr = 0o40755 << 16 | 0x10
            z.writestr(info, '')


def write_xlsx(header, rows):
    try:
        import openpyxl
        from openpyxl.styles import Font
    except ImportError:
        print('openpyxl not installed, skipping catalog/_categorylist.xlsx')
        return
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = '_categorylist'
    ws.append(header)
    for row in rows:
        ws.append([row[h] for h in header])
    for cell in ws[1]:
        cell.font = Font(bold=True)
    ws.freeze_panes = 'C2'
    ws.auto_filter.ref = ws.dimensions
    for col, width in zip('ABCDEF', (20, 22, 14, 10, 60, 80)):
        ws.column_dimensions[col].width = width
    wb.save(XLSX_FILE)


class Matcher:
    """Mirror of the app's two steps.

    Already-UCS files: first CatID in data.txt order that the name starts with.
    Other files: lowercase name, spaces -> "_", split on "_", count shared words
    with each keyword file and keep every CatID with the best score."""

    def __init__(self, rows):
        self.ordered = [r['CatID'] for r in move_order(rows)]
        self.keywords = {r['CatID']: {k.strip().lower() for k in r[SYN].split(',')} for r in rows}

    def suggest(self, file_name):
        """Returns (already_ucs_catid, [(catid, score), ...])."""
        base = os.path.basename(file_name)
        for catid in self.ordered:
            if base.startswith(catid.replace(' ', '_')):
                return catid, []
        words = set(os.path.splitext(base.lower().replace(' ', '_'))[0].split('_'))
        scores = {c: len(words & kws) for c, kws in self.keywords.items()}
        best = max(scores.values())
        if best == 0:
            return None, []
        return None, sorted((c, s) for c, s in scores.items() if s == best)


def match(rows, file_names):
    where = {r['CatID']: f"{r['Category']}/{r['SubCategory']}" for r in rows}
    matcher = Matcher(rows)
    for name in file_names:
        print(name)
        ucs, options = matcher.suggest(name)
        if ucs:
            print(f'  already UCS -> moved to {where[ucs]} ({ucs})')
        elif not options:
            print('  no match')
        for catid, score in options:
            print(f'  {catid:<12} {where[catid]}  (match level {score})')


def run_tests(rows):
    """Check catalog/match_tests.csv: the expected CatID must be offered, among at most
    max_options choices. Returns the number of failures."""
    failures = 0
    with open(os.path.join(CATALOG_DIR, 'match_tests.csv'), encoding='utf-8') as f:
        lines = [l for l in f if l.strip() and not l.startswith('#')]
    cases = list(csv.DictReader(lines))
    matcher = Matcher(rows)
    for case in cases:
        ucs, options = matcher.suggest(case['file'])
        offered = [ucs] if ucs else [c for c, _ in options]
        limit = int(case['max_options'])
        if case['expected'] not in offered or len(offered) > limit:
            failures += 1
            shown = ', '.join(offered[:8]) + (' ...' if len(offered) > 8 else '') or 'nothing'
            print(f"FAIL {case['file']}: expected {case['expected']} in max {limit}, got {len(offered)}: {shown}")
    print(f'{len(cases) - failures}/{len(cases)} match tests pass')
    return failures


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--check', action='store_true', help='validate only, write nothing')
    parser.add_argument('--match', nargs='+', metavar='FILE', help='show which CatIDs the app would suggest')
    parser.add_argument('--test', action='store_true', help='run catalog/match_tests.csv')
    args = parser.parse_args()

    header, rows = load()
    errors, warnings = validate(rows)
    for w in warnings:
        print('warning:', w)
    for e in errors:
        print('ERROR:', e)
    if errors:
        sys.exit(1)

    if args.match:
        match(rows, args.match)
        return
    if args.test:
        sys.exit(1 if run_tests(rows) else 0)
    print(f'{len(rows)} CatIDs in {len({r["Category"] for r in rows})} categories are valid')
    if args.check:
        return
    write_data(rows)
    write_keywords(rows)
    write_folders_zip(rows)
    write_xlsx(header, rows)
    print('wrote data.txt, keywords/, UCS(folders).zip and catalog/_categorylist.xlsx')


if __name__ == '__main__':
    main()
