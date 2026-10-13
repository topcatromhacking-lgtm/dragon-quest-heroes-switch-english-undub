#!/usr/bin/env python3
"""Read-only Western PC Action List pagination feasibility planner.

Usage:
 python plan_action_list_pages.py PC/0000000000000024.vap --summary page_stats.json

This does not patch the game or implement runtime page switching.
--local-preview contains copyrighted source text and must remain private.
"""
from __future__ import annotations
import argparse, collections, hashlib, json, re, struct
from pathlib import Path

BUTTON = re.compile(r'\x1bP[0-9A-Z]')
SPACES = re.compile(r'\s+')


def visible_units(s: str) -> int:
    """Conservative estimate: controller codes are single rendered icons."""
    return len(BUTTON.sub('◌', s))


def source_text(path: Path) -> list[str]:
    b = path.read_bytes()
    if b[:4] != b'\x01\x00\x00\x00' or b[12:16] != b'XL\x13\x00':
        raise ValueError('Unexpected Action List VAP header')
    packed = struct.unpack_from('<I', b, 20)[0]
    count, stride = packed & 0xffff, packed >> 16
    if count != 184 or stride != 12:
        raise ValueError('Expected exactly 184 three-column Action List rows')
    base = 12 + struct.unpack_from('<I', b, 24)[0]
    ptr = struct.unpack_from('<552I', b, base)
    if list(ptr) != sorted(ptr):
        raise ValueError('Unsorted VAP pointers')
    out = []
    for i in range(count):
        j = 3*i+2
        stop = ptr[j+1] if j+1 < len(ptr) else len(b)-base
        raw = b[base+ptr[j]:base+stop].split(b'\0', 1)[0]
        out.append(raw.decode('utf8'))
    return out


def normalize(s: str) -> str:
    return SPACES.sub(' ', s).strip()


def paginate(s: str, max_units: int = 58, max_cols: int = 39) -> list[str]:
    if not (1 <= max_cols <= max_units <= 60):
        raise ValueError('Invalid limits; original Switch primitive pool has 60')
    words = s.split()
    if not words:
        return ['']
    pages, lines, line = [], [], ''

    def flush_line():
        nonlocal line
        if line:
            lines.append(line)
            line = ''

    def finish_page():
        nonlocal lines
        flush_line()
        if lines:
            pages.append('\n'.join(lines))
            lines = []

    for word in words:
        if visible_units(word) > max_cols:
            raise ValueError('A word exceeds the allowed line width')
        choice = (line+' '+word) if line else word
        if visible_units(choice) > max_cols:
            flush_line()
            choice = word
        trial = '\n'.join(lines+[choice])
        if visible_units(trial) > max_units:
            finish_page()
            choice = word
        line = choice
    finish_page()
    if normalize(' '.join(pages)) != normalize(s):
        raise AssertionError('Wording altered or lost')
    for page in pages:
        if visible_units(page) > max_units:
            raise AssertionError('Page exceeds estimated sprite cap')
        if any(visible_units(x) > max_cols for x in page.split('\n')):
            raise AssertionError('Line exceeds width cap')
        if BUTTON.sub('', page).find('\x1b') >= 0:
            raise AssertionError('Controller icon token was split')
    return pages


def analyze(texts: list[str], max_units: int = 58, max_cols: int = 39):
    pages = [paginate(s, max_units, max_cols) for s in texts]
    distribution = collections.Counter(map(len, pages))
    info = {
        'source_records':len(texts),
        'max_source_characters':max(map(len, texts)),
        'existing_60_slot_native_pool':60,
        'planned_page_visible_unit_cap':max_units,
        'planned_line_unit_cap':max_cols,
        'page_count_distribution':{str(k):v for k,v in sorted(distribution.items())},
        'total_display_pages':sum(map(len, pages)),
        'max_pages_per_description':max(map(len, pages)),
        'descriptions_needing_multiple_pages':sum(len(p)>1 for p in pages),
        'max_page_visible_units':max(visible_units(p) for row in pages for p in row),
        'max_page_line_units':max(visible_units(line) for row in pages for p in row for line in p.split('\n')),
        'all_184_source_wording_preserved':len(texts)==184 and all(
            normalize(' '.join(p))==normalize(source) for source,p in zip(texts,pages)),
        'caveat':'Estimated sprite count only; line breaks/button codes require runtime validation'
    }
    return pages, info


def main():
    ap=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('western_pc_action_vap',type=Path)
    ap.add_argument('--max-units',type=int,default=58)
    ap.add_argument('--max-cols',type=int,default=39)
    ap.add_argument('--summary',type=Path)
    ap.add_argument('--local-preview',type=Path,help='PRIVATE text-bearing JSON, do not publish')
    args=ap.parse_args()
    source=source_text(args.western_pc_action_vap)
    pages, info=analyze(source,args.max_units,args.max_cols)
    info['input_sha256']=hashlib.sha256(args.western_pc_action_vap.read_bytes()).hexdigest()
    print(json.dumps(info,indent=2))
    if args.summary:
        args.summary.write_text(json.dumps(info,indent=2)+'\n',encoding='utf8')
    if args.local_preview:
        args.local_preview.write_text(json.dumps(
            [{'row':i,'pages':entry} for i,entry in enumerate(pages)],indent=2,
            ensure_ascii=False)+'\n',encoding='utf8')


if __name__ == '__main__':
    main()
