"""Build docs/KATALOG.md (every category, subcategory and keyword) from catalog/*.csv,
and optionally docs/UCS-katalog.pdf (user guide + catalog, ready to print).

    python tools/build_docs.py          # docs/KATALOG.md
    python tools/build_docs.py --pdf    # also docs/UCS-katalog.pdf

The PDF needs the "markdown" package and Chromium or Chrome. Set CHROME=/path/to/chrome
if it isn't found automatically.
"""
import argparse
import datetime
import glob
import html
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_catalog  # noqa: E402

ROOT = build_catalog.ROOT
DOCS_DIR = os.path.join(ROOT, 'docs')
CATALOG_MD = os.path.join(DOCS_DIR, 'KATALOG.md')
GUIDE_MD = os.path.join(DOCS_DIR, 'BRUKERVEILEDNING.md')
PDF_FILE = os.path.join(DOCS_DIR, 'UCS-katalog.pdf')
SYN = build_catalog.SYN

PARTS = [
    ('Musikkproduksjon', lambda r: r['_custom'] and r['Category'] != 'AI GENERATED'),
    ('AI GENERATED', lambda r: r['Category'] == 'AI GENERATED'),
    ('Offisiell UCS', lambda r: not r['_custom']),
]


def anchor(text):
    return ''.join(c for c in text.lower().replace(' ', '-') if c.isalnum() or c == '-')


def cell(text):
    return text.replace('|', '\\|').replace('\n', ' ').strip()


def grouped(rows):
    cats = {}
    for row in rows:
        cats.setdefault(row['Category'], []).append(row)
    return cats


def catalog_markdown(rows):
    out = ['# Kategori- og nøkkelordkatalog', '',
           '> Generert av `tools/build_docs.py` fra `catalog/*.csv`. Ikke rediger denne filen,',
           '> endre CSV-filene og kjør skriptet på nytt. Se [BRUKERVEILEDNING.md](BRUKERVEILEDNING.md).',
           '']
    total_kw = sum(len(build_catalog.keywords_of(r)) for r in rows)
    out += [f'{len(rows)} CatID-er i {len({r["Category"] for r in rows})} kategorier, {total_kw} nøkkelord.', '']
    for part, belongs in PARTS:
        part_rows = [r for r in rows if belongs(r)]
        cats = grouped(part_rows)
        out += [f'- [{part}](#{anchor(part)}) ({len(cats)} kategorier, {len(part_rows)} CatID-er)']
    out.append('')
    for part, belongs in PARTS:
        cats = grouped([r for r in rows if belongs(r)])
        out += [f'## {part}', '']
        out.append(' · '.join(f'[{c}](#{anchor(c)})' for c in cats))
        out.append('')
        for cat, cat_rows in cats.items():
            first = cat_rows[0]
            no = f' ({first["Category_no"]})' if first.get('Category_no') else ''
            out += [f'### {cat}', '', f'CatShort `{first["CatShort"]}`{no}, {len(cat_rows)} underkategorier.', '',
                    '| Underkategori | Norsk | CatID | Beskrivelse | Nøkkelord |',
                    '|---|---|---|---|---|']
            for r in cat_rows:
                out.append(f'| {cell(r["SubCategory"])} | {cell(r.get("SubCategory_no", ""))} | `{r["CatID"]}` | '
                           f'{cell(r["Explanations"])} | {cell(", ".join(build_catalog.keywords_of(r)))} |')
            out.append('')
    return '\n'.join(out)


CSS = """
@page { size: A4; margin: 16mm 14mm; }
body { font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 9.5pt; color: #1d1d1f; line-height: 1.45; }
h1 { font-size: 22pt; margin: 0 0 6mm; page-break-before: always; }
h1:first-of-type { page-break-before: avoid; }
h2 { font-size: 15pt; margin-top: 8mm; border-bottom: 1.5px solid #1d1d1f; padding-bottom: 1mm; }
h3 { font-size: 12pt; margin-top: 6mm; page-break-after: avoid; }
h4 { font-size: 10.5pt; page-break-after: avoid; }
table { border-collapse: collapse; width: 100%; margin: 2mm 0 4mm; font-size: 8.5pt; }
th, td { border: 0.5px solid #c7c7cc; padding: 1.2mm 1.6mm; vertical-align: top; text-align: left; }
th { background: #f2f2f7; }
tr { page-break-inside: avoid; }
code { font-family: Menlo, Consolas, monospace; font-size: 8.5pt; background: #f2f2f7; padding: 0 1mm; border-radius: 1mm; }
pre { background: #f2f2f7; padding: 2.5mm; border-radius: 1.5mm; font-size: 8.5pt; white-space: pre-wrap; }
pre code { background: none; padding: 0; }
blockquote { color: #6e6e73; margin: 0 0 4mm; padding-left: 3mm; border-left: 2px solid #c7c7cc; }
a { color: #1d1d1f; text-decoration: none; }
.cover { height: 250mm; display: flex; flex-direction: column; justify-content: center; }
.cover h1 { font-size: 34pt; page-break-before: avoid; }
.cover p { font-size: 12pt; color: #6e6e73; }
"""


def find_chrome():
    candidates = [os.environ.get('CHROME'), shutil.which('chromium'), shutil.which('chromium-browser'),
                  shutil.which('google-chrome'), shutil.which('chrome'), '/opt/pw-browsers/chromium',
                  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                  r'C:\Program Files\Google\Chrome\Application\chrome.exe']
    candidates += glob.glob('/opt/pw-browsers/chromium-*/chrome-linux/chrome')
    return next((c for c in candidates if c and os.path.exists(c)), None)


def build_pdf(catalog_md):
    try:
        import markdown
    except ImportError:
        sys.exit('PDF needs the markdown package: pip install markdown')
    chrome = find_chrome()
    if not chrome:
        sys.exit('PDF needs Chromium or Chrome; set CHROME=/path/to/chrome')
    with open(GUIDE_MD, encoding='utf-8') as f:
        guide_md = f.read()
    md = lambda text: markdown.markdown(text, extensions=['tables', 'fenced_code', 'toc'])
    today = datetime.date.today().isoformat()
    body = (f'<div class="cover"><h1>UCSFilesManager</h1><p>Brukerveiledning og kategori- og nøkkelordkatalog</p>'
            f'<p>{html.escape(today)}</p></div>' + md(guide_md) + md(catalog_md))
    page = f'<!doctype html><html lang="no"><head><meta charset="utf-8"><style>{CSS}</style></head><body>{body}</body></html>'
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, 'docs.html')
        with open(src, 'w', encoding='utf-8') as f:
            f.write(page)
        subprocess.run([chrome, '--headless', '--no-sandbox', '--disable-gpu', '--no-pdf-header-footer',
                        f'--print-to-pdf={PDF_FILE}', 'file://' + src],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f'wrote {os.path.relpath(PDF_FILE, ROOT)}')


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--pdf', action='store_true', help='also build docs/UCS-katalog.pdf')
    args = parser.parse_args()
    _, rows = build_catalog.load()
    text = catalog_markdown(rows)
    os.makedirs(DOCS_DIR, exist_ok=True)
    with open(CATALOG_MD, 'w', encoding='utf-8') as f:
        f.write(text + '\n')
    print(f'wrote {os.path.relpath(CATALOG_MD, ROOT)}')
    if args.pdf:
        build_pdf(text)


if __name__ == '__main__':
    main()
