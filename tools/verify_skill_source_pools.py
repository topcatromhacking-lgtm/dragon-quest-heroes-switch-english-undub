#!/usr/bin/env python3
"""Read-only M1 verifier: Western PC records and Switch 1.0.0 sprite pool instructions.

python verify_skill_source_pools.py ORIGINAL_MAIN PC_0001.vap skill_report.json
Do not patch any of the reported immediate counts without backing-memory proof.
"""
from pathlib import Path
import argparse,hashlib,json,struct
import lz4.block
EXPECTED_MAIN="cc9dfbc99f1a60120fd30b3e82dc98a17e6b2754f9cad6acfd5be329cbe63e4d"
EXPECTED_PC="05982ef0729b4245321b9b86a468f0a9bd36728da25793fd7b52fd5c5f1c74ec"
EXPECTED_SLOT3="17ffe261da8bbcc8301acf71cb057a619e318460b79071530b26f6f244cb271f"
# VA -> exact little-endian instruction word, from Japanese Switch 1.0.0.
SITES={
 0xBF58BC:0x321e07e3,0xBF59D8:0x52946408,0xBF59DC:0x8b080276,
 0xBF59E4:0x97fbe0fb,0xBF5A98:0xf9000196,0xBF5AA0:0x910d82cd,
 0xBF5AD8:0x110d818c,0xCA64B8:0x11001d49,0xCA64BC:0x6b0b013f,
 0xCA6508:0x5280090c,0xCA650C:0x9b0c2d55,0xCA6510:0xb9001d09,
 0xCA65C8:0x32000be3,0xCA668C:0x97f91dd1,0xCA66BC:0x9107e2ab}
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("original_main",type=Path);p.add_argument("pc_0001",type=Path)
 p.add_argument("report",type=Path);p.add_argument("--output",type=Path)
 a=p.parse_args()
 orig,pc=a.original_main.read_bytes(),a.pc_0001.read_bytes()
 rep=json.loads(a.report.read_text(encoding="utf8"))
 if sha(orig)!=EXPECTED_MAIN or sha(pc)!=EXPECTED_PC:raise ValueError("unexpected binary hash")
 if rep["slot_3_sha256"]!=EXPECTED_SLOT3 or rep["slot_3_message_records"]!=4501:raise ValueError("unexpected installed translated VAP report")
 if orig[:4]!=b"NSO0":raise ValueError("NSO header missing")
 off,base,size=struct.unpack_from("<III",orig,0x10)
 if base!=0 or size!=0x11b7698:raise ValueError("unexpected text segment")
 code=lz4.block.decompress(orig[off:off+struct.unpack_from("<I",orig,0x60)[0]],uncompressed_size=size) if orig[0xc]&1 else orig[off:off+size]
 for va,expected in SITES.items():
  actual=struct.unpack_from("<I",code,va)[0]
  if actual!=expected:raise ValueError(f"NSO code mismatch 0x{va:X}: 0x{actual:X}")
 packed=struct.unpack_from("<I",pc,20)[0]
 count,cols=packed&65535,(packed>>16)//4
 if (count,cols)!=(4501,8):raise ValueError("unexpected PC system text format")
 at=12+struct.unpack_from("<I",pc,24)[0]
 ptr=struct.unpack_from("<%dI"%(count*cols),pc,at)
 lines=[]
 for title,locations in rep["labels_in_system_vap"].items():
  for loc in locations:
   k=loc["record"]*cols+loc["column"];entry=pc[at+ptr[k]:].split(b"\0",1)[0].decode("utf8")
   if title=="Exclusive ESC control code":
    if not entry.startswith("\x1bF4\x1bI040"):raise ValueError("escape label mismatch")
   elif title not in entry:raise ValueError(f"source label mismatch at {loc['record']}")
   lines.append({"label":title,"record":loc["record"],"match":"exact" if entry==title else "substring_or_esc_prefix","escape_count":entry.count("\x1b")})
 result={"status":"read-only; no patch","main_sha256":EXPECTED_MAIN,"pc_sha256":EXPECTED_PC,"installed_switch_slot3_sha256":EXPECTED_SLOT3,
 "source_record_occurrences_verified":len(lines),"native_instructions_verified":len(SITES),
 "source_matches":lines,"sprite_pools":[
  {"type":"embedded","routine":"CMenuSkillCharaSelect::OnRegister","count":12,"start":"this+0xA320","registered_bytes":864},
  {"type":"global-dynamic","routine":"CUISkillEditWnd::RegisterPoint","count":7,"reserved_count":7,"registered_bytes":504}],
 "warning":"No unambiguous draw-call mapping to specific screenshot heading. No safe cap increase proven."}
 out=json.dumps(result,indent=2,ensure_ascii=False)+"\n"
 if a.output:a.output.write_text(out,encoding="utf8")
 print("Verified:",len(SITES),"instructions and",len(lines),"source label matches. No patch built.")
if __name__=="__main__":main()
