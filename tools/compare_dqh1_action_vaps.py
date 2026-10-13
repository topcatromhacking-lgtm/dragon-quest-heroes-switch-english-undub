#!/usr/bin/env python3
"""Read-only Western PC <-> Switch DQH1 Action List VAP comparison.

Example:
    python compare_dqh1_action_vaps.py PC/0000000000000024.vap SWITCH/0000000000000008.vap --json action_compare.json

No input files are modified. The script does not contain copyrighted game text.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import struct
from pathlib import Path


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def parse_vap(path: Path):
    b = path.read_bytes()
    if len(b) < 36 or b[:4] != b'\x01\x00\x00\x00' or b[12:16] != b'XL\x13\x00':
        raise ValueError(f'{path}: invalid VAP magic')
    info = struct.unpack_from('<I', b, 20)[0]
    count, stride = info & 0xffff, info >> 16
    if not count or stride != 12 or count > 65535:
        raise ValueError(f'{path}: wrong row count or record stride')
    base = 12 + struct.unpack_from('<I', b, 24)[0]
    n = count * 3
    if base + n * 4 > len(b):
        raise ValueError(f'{path}: pointer table exceeds file')
    pointers = struct.unpack_from('<' + 'I' * n, b, base)
    if pointers[0] < 4 * n or list(pointers) != sorted(pointers) or pointers[-1] >= len(b) - base:
        raise ValueError(f'{path}: invalid pointers')
    rows = []
    end_positions = list(pointers[1:]) + [len(b) - base]
    for i in range(count):
        row = []
        for j in range(3):
            k = 3 * i + j
            raw = b[base + pointers[k]:base + end_positions[k]].split(b'\x00', 1)[0]
            try:
                value = raw.decode('utf-8')
            except UnicodeDecodeError as exc:
                raise ValueError(f'{path}: text is not UTF-8 in row {i}, column {j}') from exc
            row.append(value)
        rows.append(row)
    return {'path': str(path), 'sha256': sha(b), 'size': len(b), 'count': count, 'stride': stride, 'rows': rows}


def unwrapped(s: str) -> str:
    """Treat deliberate newline wrapping as layout, not a translation change."""
    return re.sub(r'\s+', ' ', s).strip()


def compare(pc, sw):
    results = {'pc': {k:v for k,v in pc.items() if k != 'rows'},
               'switch': {k:v for k,v in sw.items() if k != 'rows'},
               'count_equal': pc['count'] == sw['count'],
               'exact_binary_equal': pc['sha256'] == sw['sha256'],
               'same_wording_rows': 0,
               'wrap_only_description_rows': [],
               'different_rows': []}
    for i in range(max(pc['count'], sw['count'])):
        if i >= min(pc['count'], sw['count']):
            results['different_rows'].append({'row':i, 'reason':'row missing from one side'})
            continue
        a,b = pc['rows'][i],sw['rows'][i]
        if a == b:
            results['same_wording_rows'] += 1
            continue
        if all(unwrapped(x) == unwrapped(y) for x,y in zip(a,b)):
            results['same_wording_rows'] += 1
            if a[2] != b[2]: results['wrap_only_description_rows'].append(i)
        else:
            changes = [j for j,(x,y) in enumerate(zip(a,b)) if unwrapped(x) != unwrapped(y)]
            results['different_rows'].append({'row':i,'different_columns':changes,
                                              'pc':a,'switch':b})
    results['all_wording_equal'] = results['count_equal'] and not results['different_rows']
    return results


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('western_pc_action_vap', type=Path)
    ap.add_argument('switch_english_action_vap', type=Path)
    ap.add_argument('--json', type=Path, dest='json_output', help='Write a JSON comparison locally')
    args = ap.parse_args()
    result=compare(parse_vap(args.western_pc_action_vap),parse_vap(args.switch_english_action_vap))
    print('PC rows:',result['pc']['count'],'Switch rows:',result['switch']['count'])
    print('Exact binary SHA match:',result['exact_binary_equal'])
    print('Unchanged wording rows:',result['same_wording_rows'])
    print('Description wrapping-only rows:',len(result['wrap_only_description_rows']))
    print('Different-content rows:',len(result['different_rows']))
    for item in result['different_rows'][:12]: print('  row',item['row'], 'columns',item.get('different_columns'), 'PC',item.get('pc'), 'SW',item.get('switch'))
    if args.json_output:
        args.json_output.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf8')
        print('Wrote:',args.json_output)


if __name__ == '__main__':
    main()
