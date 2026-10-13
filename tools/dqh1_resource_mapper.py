#!/usr/bin/env python3
"""
DQH1 PC-Western <-> Switch-JP resource mapper

Scans QuickBMS extraction folders and produces:
  inventory_pc.csv
  inventory_nsw.csv
  exact_matches.csv
  structural_candidates.csv
  likely_localization.csv
  summary.txt

It does not modify any game files.
"""

from __future__ import annotations
from pathlib import Path
import argparse
import csv
import hashlib
import math
import struct
from collections import defaultdict

CHUNK = 16 * 1024 * 1024


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(CHUNK), b""):
            h.update(b)
    return h.hexdigest()


def parse_hex_id(path: Path):
    try:
        return int(path.stem, 16)
    except ValueError:
        return None


def read_head(path: Path, n=256):
    with path.open("rb") as f:
        return f.read(n)


def printable_magic(head: bytes):
    if len(head) < 4:
        return ""
    raw = head[:4]
    if all(32 <= b < 127 for b in raw):
        return raw.decode("ascii", "replace")
    return raw.hex().upper()


def detect_vap(path: Path, head: bytes, size: int):
    # DQH VAP text banks observed so far:
    #   packed descriptor @ 0x14: high16 = record width, low16 = logical count
    #   table base = u32@0x18 + 0x0C
    if size < 0x24 or len(head) < 0x20:
        return None
    try:
        packed = struct.unpack_from("<I", head, 0x14)[0]
        count = packed & 0xFFFF
        recsize = (packed >> 16) & 0xFFFF
        base = struct.unpack_from("<I", head, 0x18)[0] + 0x0C
    except struct.error:
        return None

    if not (1 <= count <= 65535):
        return None
    if recsize < 4 or recsize > 0x100 or recsize % 4:
        return None
    if base < 0x20 or base + count * recsize > size:
        return None

    return {
        "kind": "VAP",
        "logical_count": count,
        "record_size": recsize,
        "slots": recsize // 4,
        "table_base": base,
        "structure": f"VAP:{count}:rec{recsize}",
        "logical_structure": f"VAP:{count}",
    }


def detect_dqh_dat(path: Path, head: bytes, size: int):
    # DQH multi-section DAT observed in PC 0008 / Switch 0004:
    # u32 section_count; then section_count pairs of (offset,size).
    # Each text section has a 20-byte local header and its first relative
    # string offset equals 4 * logical entry count.
    if size < 36 or len(head) < 36:
        return None
    try:
        nsec = struct.unpack_from("<I", head, 0)[0]
    except struct.error:
        return None
    if not (2 <= nsec <= 16):
        return None
    top_header = 4 + nsec * 8
    if top_header > size:
        return None

    pairs = []
    try:
        for i in range(nsec):
            off, secsize = struct.unpack_from("<II", head, 4 + i * 8)
            if off < top_header or off >= size or secsize <= 0 or off + secsize > size + 4:
                return None
            pairs.append((off, secsize))
    except struct.error:
        return None

    counts = []
    section_markers = []
    with path.open("rb") as f:
        for off, secsize in pairs:
            if off + 24 > size:
                return None
            f.seek(off)
            sh = f.read(32)
            if len(sh) < 24:
                return None
            first_rel = struct.unpack_from("<I", sh, 20)[0]
            if first_rel == 0 or first_rel % 4 or first_rel > secsize:
                counts.append(0)
            else:
                counts.append(first_rel // 4)
            section_markers.append(sh[:4].hex().upper())

    # Require at least two plausible indexed sections to avoid generic false positives.
    if sum(1 for x in counts if x > 0) < 2:
        return None

    return {
        "kind": "DAT",
        "section_count": nsec,
        "bank_counts": ",".join(str(x) for x in counts),
        "section_markers": ",".join(section_markers),
        "structure": f"DAT:{nsec}:" + ",".join(str(x) for x in counts),
        "logical_structure": f"DAT:{nsec}:" + ",".join(str(x) for x in counts),
    }


def detect_g1t(head: bytes):
    # Identification only. We intentionally do not guess undocumented
    # offsets/dimensions here.
    if head.startswith(b"_G1T") or head.startswith(b"G1T"):
        return {"kind": "G1T", "structure": "G1T", "logical_structure": "G1T"}
    return None


def inventory_one(path: Path):
    size = path.stat().st_size
    head = read_head(path)
    ext = path.suffix.lower()
    info = {
        "name": path.name,
        "id_hex": path.stem,
        "id_num": parse_hex_id(path),
        "ext": ext,
        "size": size,
        "sha256": sha256_file(path),
        "magic": printable_magic(head),
        "kind": "",
        "structure": "",
        "logical_structure": "",
        "logical_count": "",
        "record_size": "",
        "slots": "",
        "section_count": "",
        "bank_counts": "",
    }

    detected = None
    if ext == ".vap":
        detected = detect_vap(path, head, size)
    if detected is None and ext == ".dat":
        detected = detect_dqh_dat(path, head, size)
    if detected is None:
        detected = detect_g1t(head)

    if detected:
        info.update(detected)

    return info


def scan_folder(folder: Path):
    files = sorted((p for p in folder.iterdir() if p.is_file()),
                   key=lambda p: (parse_hex_id(p) is None, parse_hex_id(p) or 0, p.name))
    rows = []
    total = len(files)
    for i, p in enumerate(files, 1):
        if i == 1 or i % 100 == 0 or i == total:
            print(f"  [{i:4d}/{total}] {p.name}")
        rows.append(inventory_one(p))
    return rows


def write_csv(path: Path, rows, fields):
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def size_score(a, b):
    if not a or not b:
        return 0.0
    ratio = min(a, b) / max(a, b)
    return 20.0 * ratio


def candidate_score(pc, sw):
    score = 0.0
    reasons = []

    if pc["sha256"] == sw["sha256"]:
        return 1000.0, ["SHA256 exact"]

    if pc["ext"] == sw["ext"]:
        score += 8
        reasons.append("same extension")
    else:
        return -1, []

    if pc["magic"] and pc["magic"] == sw["magic"]:
        score += 5
        reasons.append("same magic")

    # Strong known DQH text structures.
    if pc["kind"] == "VAP" and sw["kind"] == "VAP":
        if pc["logical_count"] == sw["logical_count"]:
            score += 70
            reasons.append(f"same VAP logical count {pc['logical_count']}")
        if pc["record_size"] == sw["record_size"]:
            score += 15
            reasons.append(f"same VAP record width {pc['record_size']}")
        elif pc["logical_count"] == sw["logical_count"]:
            reasons.append(f"VAP width {pc['record_size']}→{sw['record_size']}")

    elif pc["kind"] == "DAT" and sw["kind"] == "DAT":
        if pc["section_count"] == sw["section_count"]:
            score += 15
            reasons.append(f"same DAT section count {pc['section_count']}")
        if pc["bank_counts"] and pc["bank_counts"] == sw["bank_counts"]:
            score += 70
            reasons.append(f"same DAT banks {pc['bank_counts']}")

    elif pc["kind"] == "G1T" and sw["kind"] == "G1T":
        score += 25
        reasons.append("both G1T")

    score += size_score(pc["size"], sw["size"])
    reasons.append(f"size ratio {min(pc['size'],sw['size'])/max(pc['size'],sw['size']):.3f}")
    return score, reasons


def unique_exact_matches(pc_rows, sw_rows):
    p = defaultdict(list)
    s = defaultdict(list)
    for r in pc_rows:
        p[r["sha256"]].append(r)
    for r in sw_rows:
        s[r["sha256"]].append(r)

    exact = []
    for h, prs in p.items():
        srs = s.get(h, [])
        if len(prs) == 1 and len(srs) == 1:
            exact.append({
                "pc_name": prs[0]["name"],
                "pc_id": prs[0]["id_num"],
                "nsw_name": srs[0]["name"],
                "nsw_id": srs[0]["id_num"],
                "size": prs[0]["size"],
                "sha256": h,
                "delta": (srs[0]["id_num"] - prs[0]["id_num"])
                         if prs[0]["id_num"] is not None and srs[0]["id_num"] is not None else "",
            })
    exact.sort(key=lambda r: (r["pc_id"] is None, r["pc_id"] or 0))
    return exact


def structural_candidates(pc_rows, sw_rows, topn=5):
    sw_by_ext = defaultdict(list)
    for r in sw_rows:
        sw_by_ext[r["ext"]].append(r)

    all_rows = []
    best_rows = []

    for p in pc_rows:
        scored = []
        for s in sw_by_ext.get(p["ext"], []):
            score, reasons = candidate_score(p, s)
            if score < 0:
                continue
            scored.append((score, s, "; ".join(reasons)))
        scored.sort(key=lambda x: (-x[0], abs(x[1]["size"] - p["size"]), x[1]["name"]))

        for rank, (score, s, reasons) in enumerate(scored[:topn], 1):
            row = {
                "pc_name": p["name"],
                "pc_id": p["id_num"],
                "pc_kind": p["kind"],
                "pc_structure": p["structure"],
                "pc_size": p["size"],
                "rank": rank,
                "score": round(score, 2),
                "nsw_name": s["name"],
                "nsw_id": s["id_num"],
                "nsw_kind": s["kind"],
                "nsw_structure": s["structure"],
                "nsw_size": s["size"],
                "reasons": reasons,
            }
            all_rows.append(row)
            if rank == 1:
                best_rows.append(row)

    return all_rows, best_rows


def likely_localization(best_rows):
    out = []
    for r in best_rows:
        # Keep strong structured non-identical candidates.
        if r["score"] >= 75 and (r["pc_kind"] in ("VAP", "DAT", "G1T") or r["nsw_kind"] in ("VAP", "DAT", "G1T")):
            out.append(r)
    out.sort(key=lambda r: (-r["score"], r["pc_id"] if r["pc_id"] is not None else 10**9))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pc_unpack", type=Path)
    ap.add_argument("nsw_unpack", type=Path)
    ap.add_argument("output", nargs="?", type=Path, default=Path("DQH1_resource_map"))
    args = ap.parse_args()

    if not args.pc_unpack.is_dir():
        raise SystemExit(f"PC folder not found: {args.pc_unpack}")
    if not args.nsw_unpack.is_dir():
        raise SystemExit(f"Switch folder not found: {args.nsw_unpack}")

    args.output.mkdir(parents=True, exist_ok=True)

    print("Scanning PC extraction...")
    pc = scan_folder(args.pc_unpack)
    print("Scanning Switch extraction...")
    sw = scan_folder(args.nsw_unpack)

    inv_fields = [
        "name","id_hex","id_num","ext","size","sha256","magic","kind",
        "structure","logical_structure","logical_count","record_size","slots",
        "section_count","bank_counts"
    ]
    write_csv(args.output / "inventory_pc.csv", pc, inv_fields)
    write_csv(args.output / "inventory_nsw.csv", sw, inv_fields)

    exact = unique_exact_matches(pc, sw)
    write_csv(args.output / "exact_matches.csv", exact,
              ["pc_name","pc_id","nsw_name","nsw_id","size","sha256","delta"])

    candidates, best = structural_candidates(pc, sw)
    cand_fields = [
        "pc_name","pc_id","pc_kind","pc_structure","pc_size","rank","score",
        "nsw_name","nsw_id","nsw_kind","nsw_structure","nsw_size","reasons"
    ]
    write_csv(args.output / "structural_candidates.csv", candidates, cand_fields)

    likely = likely_localization(best)
    write_csv(args.output / "likely_localization.csv", likely, cand_fields)

    known = [
        ("0000000000000001.vap", "0000000000000003.vap", "menu/system text", "CONFIRMED"),
        ("0000000000000008.dat", "0000000000000004.dat", "gameplay/story text", "CONFIRMED"),
        ("00000000000000bc.vap", "0000000000000064.vap", "cutscene subtitles", "CONFIRMED"),
    ]

    summary = [
        "DQH1 PC-Western <-> Switch-JP resource map",
        "==========================================",
        "",
        f"PC resources scanned:     {len(pc)}",
        f"Switch resources scanned: {len(sw)}",
        f"Unique exact hash pairs:  {len(exact)}",
        f"Strong structured candidates: {len(likely)}",
        "",
        "Known confirmed localization pairs:",
    ]
    for a,b,role,status in known:
        summary.append(f"  {a}  <->  {b}   {role}   [{status}]")

    if exact:
        deltas = defaultdict(int)
        for r in exact:
            if r["delta"] != "":
                deltas[r["delta"]] += 1
        summary += ["", "Most common ID deltas among unique exact matches:"]
        for d,n in sorted(deltas.items(), key=lambda kv: (-kv[1], kv[0]))[:15]:
            summary.append(f"  {d:+d}: {n} exact pairs")

    summary += [
        "",
        "Files written:",
        "  inventory_pc.csv",
        "  inventory_nsw.csv",
        "  exact_matches.csv",
        "  structural_candidates.csv",
        "  likely_localization.csv",
        "",
        "Upload these CSV/TXT outputs to ChatGPT for the next mapping pass.",
    ]

    (args.output / "summary.txt").write_text("\n".join(summary) + "\n", encoding="utf-8")

    print()
    print("\n".join(summary))


if __name__ == "__main__":
    main()