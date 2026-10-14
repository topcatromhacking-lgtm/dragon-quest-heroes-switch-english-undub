#!/usr/bin/env python3
"""Read-only M1 audit of DQH1 Switch skill-tree font call sites.

Usage:
  python audit_skill_ui_capacity.py original-Switch-1.0.0-exefs-main PC/0000000000000001.vap

Inputs must be user-extracted. Never modifies executable or game text.
A validated w3 immediate near a font call does NOT establish its backing
sprite-buffer size or prove that the value reaches the call along every path.
"""
import argparse,hashlib,json,struct
from pathlib import Path

MAIN_SHA="cc9dfbc99f1a60120fd30b3e82dc98a17e6b2754f9cad6acfd5be329cbe63e4d"
PC_SHA="05982ef0729b4245321b9b86a468f0a9bd36728da25793fd7b52fd5c5f1c74ec"
FONT=0xAEDDD0
# label, w3 immediate address, immediate instruction, SetStrPrim BL address
SITES=[
 ("CharacterSelect",0xBF58BC,0x321E07E3,0xBF59E4),
 ("SkillName",0xB38D74,0x52800243,0xB38DA8),
 ("Effect_A",0xB391FC,0x528000A3,0xB39294),
 ("Effect_B",0xB39450,0x321C07E3,0xB394EC),
 ("Learn_A",0xB39B3C,0x321F07E3,0xB39BD4),
 ("Learn_B",0xB39E24,0x321C07E3,0xB39EC0),
 ("Learn_C",0xB3A024,0x321F03E3,0xB3A0BC),
 ("Learn_D",0xB3A2FC,0x321C07E3,0xB3A32C),
 ("InfoPoint_A",0xB3A4BC,0x321F07E3,0xB3A5E4),
 ("InfoPoint_B",0xB3A708,0x321E03E3,0xB3A844),
 ("InfoPoint_C",0xB3AA2C,0x320003E3,0xB3AAC4),
 ("SkillPoint_A",0xCA65C8,0x32000BE3,0xCA668C),
 ("SkillPoint_B",0xCA6854,0x321E03E3,0xCA6960),
 ("SkillPoint_C",0xCA6B7C,0x320003E3,0xCA6BB0),
]
LABELS=("Attributes","Requirements","Points Required","Skill Points",
        "Switch Character","Spells and Abilities")

def digest(b):return hashlib.sha256(b).hexdigest()

def load_text(path):
    b=path.read_bytes()
    if digest(b)!=MAIN_SHA:raise ValueError("Not known-original Japanese Switch 1.0.0 NSO")
    if b[:4]!=b"NSO0":raise ValueError("NSO header mismatch")
    offset,vaddr,expected=struct.unpack_from("<III",b,0x10)
    packed_size=struct.unpack_from("<I",b,0x60)[0]
    if vaddr!=0 or expected!=0x11B7698:raise ValueError("NSO text layout mismatch")
    if b[0xC]&1:
        import lz4.block
        text=lz4.block.decompress(b[offset:offset+packed_size],uncompressed_size=expected)
    else:text=b[offset:offset+expected]
    if len(text)!=expected:raise ValueError("Decompressed code size mismatch")
    return text

def audit(main,pc):
    text=load_text(main)
    pc_bytes=pc.read_bytes()
    if digest(pc_bytes)!=PC_SHA:raise ValueError("Western PC source mismatch")
    source={s:pc_bytes.count(s.encode()) for s in LABELS}
    if any(v==0 for v in source.values()):raise ValueError("Missing Western PC title")
    rows=[]
    for name,at,expected,call in SITES:
        word=struct.unpack_from("<I",text,at)[0]
        bl=struct.unpack_from("<I",text,call)[0]
        if word!=expected:raise ValueError("Immediate mismatch at "+hex(at))
        if bl>>26!=0b100101:raise ValueError("No BL instruction at "+hex(call))
        delta=bl&0x3FFFFFF
        if delta&0x2000000:delta-=0x4000000
        if call+4*delta!=FONT:raise ValueError("Unexpected font target at "+hex(call))
        rows.append({"routine":name,"nearby_w3_instruction":hex(at),
                     "font_call":hex(call),"direct_target":hex(FONT)})
    return {"verified_original_nso":MAIN_SHA,"verified_pc_source":PC_SHA,
            "western_pc_labels_raw_occurrences":source,
            "verified_call_site_pairs":rows,
            "call_pairs_checked":len(rows),
            "warning":"No backing pool size, reachability for every branch, or per-title call linkage proved. Do not change immediate counts."}

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("original_switch_main",type=Path)
    p.add_argument("western_pc_0001_vap",type=Path)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    report=audit(a.original_switch_main,a.western_pc_0001_vap)
    encoded=json.dumps(report,indent=2)+"\n"
    print(encoded,end="")
    if a.output:a.output.write_text(encoded,encoding="utf-8")
