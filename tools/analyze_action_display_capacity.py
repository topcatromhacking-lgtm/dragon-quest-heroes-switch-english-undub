#!/usr/bin/env python3
"""Read-only DQH1 Japanese Switch 1.0.0 Action List primitive-capacity audit.

Usage:
 python analyze_action_display_capacity.py /path/to/Switch/main --action /path/to/English/0000000000000008.vap

Requires 'lz4' package for compressed NSOs. No game assets are distributed.
Do not use these instruction signatures for other Switch title versions.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import struct

# Instruction signatures for Japanese Switch v1.0.0, verified offline.
CHECKS = {
    'Register.limit60': (0x251C1C, 'e30f1e32'),
    'Register.callSetStrPrim': (0x251C30, '2d27fe97'),
    'Constructor.allocate4320': (0x24FB84, '0f1c8252'),
    'Constructor.step72': (0x24FC24, '29210191'),
    'Constructor.arrayBoundary': (0x24FC28, '3f010feb'),
    'Constructor.nextMember': (0x24FC88, '6c6e22f9'),
    'Font.captureLimit': (0x1DB918, 'f403032a'),
    'Font.limitCheck1': (0x1DBE14, '1f03146b'),
    'Font.limitCheck2': (0x1DC6C4, '1f03146b'),
}

def read_text(path):
    raw = path.read_bytes()
    if raw[:4] != b'NSO0':
        raise ValueError('Not an NSO main executable')
    off, base, size = struct.unpack_from('<3I', raw, 0x10)
    flag = struct.unpack_from('<I', raw, 0x0c)[0]
    if flag & 1:
        from lz4.block import decompress
        stored = struct.unpack_from('<I', raw, 0x60)[0]
        code = decompress(raw[off:off + stored], uncompressed_size=size)
    else:
        code = raw[off:off + size]
    if base != 0 or len(code) != size:
        raise ValueError('Unexpected NSO text mapping')
    return code, hashlib.sha256(raw).hexdigest()

def read_action_counts(path):
    raw = path.read_bytes()
    if raw[:4] != b'\x01\0\0\0' or raw[12:16] != b'XL\x13\0':
        raise ValueError('Unexpected Action VAP header')
    packed = struct.unpack_from('<I', raw, 20)[0]
    count, stride = packed & 65535, packed >> 16
    base = 12 + struct.unpack_from('<I', raw, 24)[0]
    if count != 184 or stride != 12:
        raise ValueError('Expected 184 three-column Action List records')
    pointers = struct.unpack_from('<' + str(count*3) + 'I', raw, base)
    lengths = []
    for i in range(count):
        k = 3*i+2
        start = base + pointers[k]
        end = base + (pointers[k+1] if k+1 < len(pointers) else len(raw)-base)
        s = raw[start:end].split(b'\0')[0].decode('utf8')
        lengths.append((len(s), len(re.sub(r'\x1bP[0-9A-Z]', '*', s))))
    return {'records':count, 'over_60_unicode_chars':sum(x>60 for x,y in lengths),
            'over_60_approximate_render_units':sum(y>60 for x,y in lengths),
            'longest_unicode_characters':max(x for x,y in lengths)}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('switch_main', type=Path)
    p.add_argument('--action', type=Path, help='Optional English-transplanted Action VAP')
    p.add_argument('--json', type=Path, help='Save source-text-free report')
    a = p.parse_args()
    code, digest = read_text(a.switch_main)
    failed = [name for name,(addr,signature) in CHECKS.items()
              if code[addr:addr+4].hex() != signature]
    if failed:
        raise SystemExit('STOP: NSO does not match verified Switch v1.0.0 code: ' + ', '.join(failed))
    assert 0x33f8 + 60*72 == 0x44d8
    result = {'main_sha256':digest,'verified_instructions':len(CHECKS),
              'description_primitive_capacity':60,'bytes_per_primitive':72,
              'sprite_array_start':'0x33F8','next_member':'0x44D8',
              'warning':'Do not increase 60 without relocating the following menu member'}
    if a.action:
        result['action_vap'] = read_action_counts(a.action)
    print(json.dumps(result, indent=2))
    if a.json:
        a.json.write_text(json.dumps(result, indent=2), encoding='utf8')

if __name__ == '__main__':
    main()
