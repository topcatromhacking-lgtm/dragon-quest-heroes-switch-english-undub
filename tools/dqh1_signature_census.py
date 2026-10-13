#!/usr/bin/env python3
"""
DQH1 resource signature census
==============================
Read-only scanner for QuickBMS PC/Switch extraction folders.

It looks beyond _G1T and inventories:
- file extensions
- first 4/8-byte signatures
- known embedded resource signatures
- likely compressed/wrapped resources
- size ranges

Outputs:
  extension_stats_pc.csv
  extension_stats_nsw.csv
  magic_census_pc.csv
  magic_census_nsw.csv
  known_signatures_pc.csv
  known_signatures_nsw.csv
  wrapper_candidates_pc.csv
  wrapper_candidates_nsw.csv
  summary.txt
"""

from pathlib import Path
import argparse, csv, math, struct
from collections import Counter, defaultdict

CHUNK = 8 * 1024 * 1024

KNOWN = {
    b"_G1T": "Koei Tecmo G1T texture",
    b"G1TG": "possible G1T variant",
    b"GT1G": "possible G1T variant",
    b"G1M_": "Koei Tecmo G1M model/container",
    b"G1MF": "Koei Tecmo G1M format block",
    b"G1MG": "Koei Tecmo G1M geometry",
    b"G1MS": "Koei Tecmo G1M skeleton",
    b"G1MM": "Koei Tecmo G1M material",
    b"KTSC": "Koei Tecmo container/signature",
    b"KTSR": "Koei Tecmo sound resource",
    b"KTGL": "Koei Tecmo graphics/resource",
    b"DDS ": "DirectDraw Surface texture",
    b"\x89PNG": "PNG image",
    b"JFIF": "JPEG/JFIF",
    b"OggS": "Ogg audio",
    b"RIFF": "RIFF/WAV/AVI",
    b"@UTF": "CRI UTF table",
    b"CPK ": "CRI CPK archive",
    b"AFS2": "CRI AFS2 audio archive",
    b"HCA\x00": "CRI HCA audio",
    b"ADX\x00": "CRI ADX audio",
    b"FARC": "FARC archive",
    b"FSB5": "FMOD sound bank",
    b"BKHD": "Wwise sound bank",
    b"AKPK": "Wwise package",
    b"PK\x03\x04": "ZIP",
    b"7z\xBC\xAF": "7-Zip",
    b"\x1F\x8B\x08": "gzip",
}

def hid(p):
    try:
        return int(p.stem, 16)
    except Exception:
        return None

def printable_sig(b):
    return ''.join(chr(x) if 32 <= x < 127 else '.' for x in b)

def entropy_sample(path, sample=65536):
    with path.open("rb") as f:
        data = f.read(sample)
    if not data:
        return 0.0
    c = Counter(data)
    n = len(data)
    return -sum((v/n)*math.log2(v/n) for v in c.values())

def find_known(path):
    hits = []
    with path.open("rb") as f:
        pos = 0
        tail = b""
        maxsig = max(len(k) for k in KNOWN)
        while True:
            block = f.read(CHUNK)
            if not block:
                break
            data = tail + block
            base = pos - len(tail)
            for sig, desc in KNOWN.items():
                start = 0
                while True:
                    i = data.find(sig, start)
                    if i < 0:
                        break
                    hits.append((base+i, sig, desc))
                    start = i + 1
            tail = data[-maxsig:]
            pos += len(block)
    # dedupe boundary-overlap duplicates
    out = {}
    for off,sig,desc in hits:
        out[(off,sig)] = desc
    return sorted((off,sig,desc) for (off,sig),desc in out.items())

def scan(folder, label):
    files = sorted([p for p in folder.iterdir() if p.is_file()],
                   key=lambda p: (hid(p) is None, hid(p) or 0, p.name))
    magic_rows = []
    known_rows = []
    wrapper_rows = []
    ext_counter = Counter()
    ext_bytes = Counter()

    for i,p in enumerate(files,1):
        if i == 1 or i % 100 == 0 or i == len(files):
            print(f"{label}: [{i}/{len(files)}] {p.name}")

        size = p.stat().st_size
        ext = p.suffix.lower() or "<none>"
        ext_counter[ext] += 1
        ext_bytes[ext] += size

        with p.open("rb") as f:
            head = f.read(32)

        sig4 = head[:4].hex().upper()
        sig8 = head[:8].hex().upper()

        magic_rows.append({
            "file": p.name,
            "id_num": hid(p),
            "ext": ext,
            "size": size,
            "sig4_hex": sig4,
            "sig4_ascii": printable_sig(head[:4]),
            "sig8_hex": sig8,
            "sig8_ascii": printable_sig(head[:8]),
            "entropy64k": round(entropy_sample(p), 4),
        })

        khits = find_known(p)
        for off,sig,desc in khits:
            known_rows.append({
                "file": p.name,
                "id_num": hid(p),
                "ext": ext,
                "size": size,
                "offset": off,
                "signature_hex": sig.hex().upper(),
                "signature_ascii": printable_sig(sig),
                "description": desc,
            })

        # Wrapper/compression candidate heuristic:
        # non-text-ish high entropy, no known signature, medium/large file.
        ent = magic_rows[-1]["entropy64k"]
        if size >= 4096 and ent >= 7.2 and not khits:
            wrapper_rows.append({
                "file": p.name,
                "id_num": hid(p),
                "ext": ext,
                "size": size,
                "sig4_hex": sig4,
                "sig4_ascii": printable_sig(head[:4]),
                "sig8_hex": sig8,
                "sig8_ascii": printable_sig(head[:8]),
                "entropy64k": ent,
            })

    ext_rows = []
    for ext,count in sorted(ext_counter.items(), key=lambda kv:(-kv[1],kv[0])):
        ext_rows.append({
            "ext": ext,
            "count": count,
            "total_bytes": ext_bytes[ext],
            "avg_bytes": round(ext_bytes[ext]/count,2),
        })

    return ext_rows, magic_rows, known_rows, wrapper_rows

def write(path, rows, fields):
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k:r.get(k,"") for k in fields})

def census(magic_rows):
    c = Counter((r["sig4_hex"], r["sig4_ascii"]) for r in magic_rows)
    out = []
    for (hx,asc),count in c.most_common():
        sizes = [r["size"] for r in magic_rows if r["sig4_hex"] == hx]
        out.append({
            "sig4_hex": hx,
            "sig4_ascii": asc,
            "count": count,
            "min_size": min(sizes),
            "max_size": max(sizes),
            "avg_size": round(sum(sizes)/len(sizes),2),
        })
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pc_unpack", type=Path)
    ap.add_argument("nsw_unpack", type=Path)
    ap.add_argument("output", nargs="?", type=Path, default=Path("DQH1_signature_map"))
    args = ap.parse_args()

    for p in (args.pc_unpack,args.nsw_unpack):
        if not p.is_dir():
            raise SystemExit(f"Folder not found: {p}")

    args.output.mkdir(parents=True, exist_ok=True)

    pc_ext, pc_magic, pc_known, pc_wrap = scan(args.pc_unpack,"PC")
    sw_ext, sw_magic, sw_known, sw_wrap = scan(args.nsw_unpack,"NSW")

    write(args.output/"extension_stats_pc.csv",pc_ext,["ext","count","total_bytes","avg_bytes"])
    write(args.output/"extension_stats_nsw.csv",sw_ext,["ext","count","total_bytes","avg_bytes"])

    write(args.output/"file_headers_pc.csv",pc_magic,
          ["file","id_num","ext","size","sig4_hex","sig4_ascii","sig8_hex","sig8_ascii","entropy64k"])
    write(args.output/"file_headers_nsw.csv",sw_magic,
          ["file","id_num","ext","size","sig4_hex","sig4_ascii","sig8_hex","sig8_ascii","entropy64k"])

    write(args.output/"magic_census_pc.csv",census(pc_magic),
          ["sig4_hex","sig4_ascii","count","min_size","max_size","avg_size"])
    write(args.output/"magic_census_nsw.csv",census(sw_magic),
          ["sig4_hex","sig4_ascii","count","min_size","max_size","avg_size"])

    write(args.output/"known_signatures_pc.csv",pc_known,
          ["file","id_num","ext","size","offset","signature_hex","signature_ascii","description"])
    write(args.output/"known_signatures_nsw.csv",sw_known,
          ["file","id_num","ext","size","offset","signature_hex","signature_ascii","description"])

    write(args.output/"wrapper_candidates_pc.csv",pc_wrap,
          ["file","id_num","ext","size","sig4_hex","sig4_ascii","sig8_hex","sig8_ascii","entropy64k"])
    write(args.output/"wrapper_candidates_nsw.csv",sw_wrap,
          ["file","id_num","ext","size","sig4_hex","sig4_ascii","sig8_hex","sig8_ascii","entropy64k"])

    summary = [
        "DQH1 resource signature census",
        "==============================",
        "",
        f"PC files: {len(pc_magic)}",
        f"Switch files: {len(sw_magic)}",
        f"PC known-signature hits: {len(pc_known)}",
        f"Switch known-signature hits: {len(sw_known)}",
        f"PC high-entropy unknown wrappers: {len(pc_wrap)}",
        f"Switch high-entropy unknown wrappers: {len(sw_wrap)}",
        "",
        "Upload these first:",
        "  summary.txt",
        "  extension_stats_pc.csv",
        "  extension_stats_nsw.csv",
        "  magic_census_pc.csv",
        "  magic_census_nsw.csv",
        "  known_signatures_pc.csv",
        "  known_signatures_nsw.csv",
        "",
        "If needed next:",
        "  wrapper_candidates_pc.csv",
        "  wrapper_candidates_nsw.csv",
        "  file_headers_pc.csv",
        "  file_headers_nsw.csv",
    ]
    (args.output/"summary.txt").write_text("\n".join(summary)+"\n",encoding="utf-8")
    print()
    print("\n".join(summary))

if __name__=="__main__":
    main()