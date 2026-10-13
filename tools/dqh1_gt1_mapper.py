#!/usr/bin/env python3
"""
DQH1 GT1G mapper
================
Maps PC-Western .gt1 texture containers to Switch-JP .gt1 containers.

Read-only. It does not modify any game files.

Outputs:
  gt1_pc.csv
  gt1_nsw.csv
  gt1_exact.csv
  gt1_candidates.csv
  gt1_priority.csv
  summary.txt
"""

from pathlib import Path
import argparse, csv, hashlib
from collections import defaultdict, Counter

CHUNK = 16 * 1024 * 1024

def hex_id(path):
    try:
        return int(path.stem, 16)
    except Exception:
        return None

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(CHUNK), b""):
            h.update(b)
    return h.hexdigest()

def header(path, n=0x80):
    with path.open("rb") as f:
        return f.read(n)

def scan(folder, label):
    files = sorted(folder.glob("*.gt1"), key=lambda p: hex_id(p) or 0)
    rows = []
    for i,p in enumerate(files,1):
        if i == 1 or i % 50 == 0 or i == len(files):
            print(f"{label}: [{i}/{len(files)}] {p.name}")
        h = header(p)
        rows.append({
            "file": p.name,
            "id": hex_id(p),
            "size": p.stat().st_size,
            "sha256": sha256(p),
            "magic": h[:4].decode("ascii","replace"),
            "version": h[4:8].decode("ascii","replace"),
            "hdr16": h[:16].hex().upper(),
            "hdr32": h[:32].hex().upper(),
            "hdr64": h[:64].hex().upper(),
        })
    return rows

def write(path, rows, fields):
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        w=csv.DictWriter(f,fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k:r.get(k,"") for k in fields})

def nearest_anchor(pid, anchors):
    if not anchors:
        return None
    return min(anchors, key=lambda a: abs(pid-a[0]))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("pc_unpack", type=Path)
    ap.add_argument("nsw_unpack", type=Path)
    ap.add_argument("output", nargs="?", type=Path, default=Path("DQH1_gt1_map"))
    args=ap.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)

    pc=scan(args.pc_unpack,"PC")
    sw=scan(args.nsw_unpack,"NSW")

    fields=["file","id","size","sha256","magic","version","hdr16","hdr32","hdr64"]
    write(args.output/"gt1_pc.csv",pc,fields)
    write(args.output/"gt1_nsw.csv",sw,fields)

    # Unique exact matches are our strongest archive-position anchors.
    pby=defaultdict(list); sby=defaultdict(list)
    for r in pc:pby[r["sha256"]].append(r)
    for r in sw:sby[r["sha256"]].append(r)

    exact=[]
    anchors=[]
    for h,prs in pby.items():
        srs=sby.get(h,[])
        if len(prs)==1 and len(srs)==1:
            p=prs[0]; s=srs[0]
            d=s["id"]-p["id"]
            exact.append({
                "pc_file":p["file"],"pc_id":p["id"],
                "nsw_file":s["file"],"nsw_id":s["id"],
                "size":p["size"],"delta":d,"sha256":h
            })
            anchors.append((p["id"],s["id"],d))

    exact.sort(key=lambda r:r["pc_id"])
    write(args.output/"gt1_exact.csv",exact,
          ["pc_file","pc_id","nsw_file","nsw_id","size","delta","sha256"])

    # Delta frequencies among exact GT1 matches.
    delta_counts=Counter(r["delta"] for r in exact)
    common_deltas=[d for d,n in delta_counts.most_common(20)]

    sw_by_id={r["id"]:r for r in sw}
    candidates=[]

    for p in pc:
        # Skip exact-identical PC resource itself.
        if any(e["pc_id"]==p["id"] for e in exact):
            continue

        predicted=[]

        na=nearest_anchor(p["id"],anchors)
        if na:
            apc,answ,d=na
            predicted.append((p["id"]+d, 35, f"nearest exact GT1 anchor {apc:04X}->{answ:04X}, delta {d:+d}"))

        for d in common_deltas:
            freq=delta_counts[d]
            predicted.append((p["id"]+d, min(25,5+freq), f"exact-GT1 delta {d:+d} seen {freq}x"))

        seen=set()
        for sid,bonus,why in predicted:
            if sid in seen or sid not in sw_by_id:
                continue
            seen.add(sid)
            s=sw_by_id[sid]

            ratio=min(p["size"],s["size"])/max(p["size"],s["size"])
            score=bonus + ratio*30
            reasons=[why,f"size ratio {ratio:.4f}"]

            if p["version"]==s["version"]:
                score+=5
                reasons.append(f"same version {p['version']}")

            # GT1 container structural prefix comparison.
            # Ignore bytes 8-15, which often contain size/count-like values.
            if p["hdr32"][0:16] == s["hdr32"][0:16]:
                score+=5
                reasons.append("same first 8 header bytes")
            if p["hdr64"][32:64] == s["hdr64"][32:64]:
                score+=10
                reasons.append("matching header bytes 0x10-0x1F")

            # Same size can be an excellent clue for platform-identical geometry/layout
            # even when texture pixels differ.
            if p["size"]==s["size"]:
                score+=15
                reasons.append("exact same file size")

            candidates.append({
                "pc_file":p["file"],"pc_id":p["id"],"pc_size":p["size"],
                "nsw_file":s["file"],"nsw_id":s["id"],"nsw_size":s["size"],
                "score":round(score,2),
                "reasons":"; ".join(reasons)
            })

    # Keep only best row per PC/Switch combination and rank.
    uniq={}
    for r in candidates:
        k=(r["pc_id"],r["nsw_id"])
        if k not in uniq or r["score"]>uniq[k]["score"]:
            uniq[k]=r
    candidates=list(uniq.values())
    candidates.sort(key=lambda r:(-r["score"],r["pc_id"],r["nsw_id"]))

    cfields=["pc_file","pc_id","pc_size","nsw_file","nsw_id","nsw_size","score","reasons"]
    write(args.output/"gt1_candidates.csv",candidates,cfields)

    # High-confidence mapping candidates.
    priority=[r for r in candidates if r["score"]>=70]
    write(args.output/"gt1_priority.csv",priority,cfields)

    # Also surface PC groups of 7 consecutive GT1s with similar sizes.
    groups=[]
    byid={r["id"]:r for r in pc}
    for start in sorted(byid):
        seq=[byid.get(start+i) for i in range(7)]
        if all(seq):
            sizes=[x["size"] for x in seq]
            if min(sizes)/max(sizes) >= 0.70:
                groups.append({
                    "start_id":start,
                    "end_id":start+6,
                    "files":" | ".join(x["file"] for x in seq),
                    "sizes":" | ".join(str(x["size"]) for x in seq),
                    "size_ratio":round(min(sizes)/max(sizes),4),
                })
    write(args.output/"gt1_pc_language_groups.csv",groups,
          ["start_id","end_id","files","sizes","size_ratio"])

    lines=[
        "DQH1 GT1G mapper",
        "================",
        "",
        f"PC GT1 files: {len(pc)}",
        f"Switch GT1 files: {len(sw)}",
        f"Unique exact GT1 pairs: {len(exact)}",
        f"Priority non-identical mappings: {len(priority)}",
        f"Possible PC 7-file language groups: {len(groups)}",
        "",
        "Exact GT1 delta frequencies:",
    ]
    for d,n in delta_counts.most_common(15):
        lines.append(f"  {d:+d}: {n}")
    lines += [
        "",
        "Upload:",
        "  summary.txt",
        "  gt1_priority.csv",
        "  gt1_exact.csv",
        "  gt1_pc_language_groups.csv",
    ]
    (args.output/"summary.txt").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print()
    print("\n".join(lines))

if __name__=="__main__":
    main()