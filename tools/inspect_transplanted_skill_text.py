#!/usr/bin/env python3
"""Read-only DQH1 skill-label inventory on an installed English-transplanted RomFS.

Example (PowerShell):
  python -X utf8 inspect_transplanted_skill_text.py "C:\\...\\romfs\\dqh1" --output skill_report.json

Default checks the DQH1 system VAP (LINKDATA slot 0x3). Optional --scan-all
searches all UNCOMPRESSED LINKDATA slot contents for the six target labels.
Never writes to the input directory or modifies assets; report is metadata only.
"""
from __future__ import annotations
import argparse,bisect,hashlib,json,struct
from pathlib import Path

TARGETS={
 'Attributes':b'Attributes',
 'Requirements':b'Requirements',
 'Points Required':b'Points Required',
 'Skill Points':b'Skill Points',
 'Switch Character':b'Switch Character',
 'Spells and Abilities':b'Spells and Abilities',
 'Exclusive ESC control code':b'\x1bF4\x1bI040-Exclusive',
}

def sha(b):return hashlib.sha256(b).hexdigest()

def idx_records(raw):
    if len(raw)%32:raise ValueError('LINKDATA.IDX alignment invalid')
    return [struct.unpack_from('<4Q',raw,i*32) for i in range(len(raw)//32)]

def occurrences(blob,query):
    pos=0
    while True:
        j=blob.find(query,pos)
        if j<0:break
        yield j
        pos=j+1

def parse_records(blob):
    if blob[:4]!=b'\x01\0\0\0' or blob[12:16]!=b'XL\x13\0':
        raise ValueError('Slot 3 not recognized as VAP')
    info=struct.unpack_from('<I',blob,20)[0]
    count,stride=info & 65535,info>>16
    base=12+struct.unpack_from('<I',blob,24)[0]
    if not count or stride!=12 or base+count*12>len(blob):
        raise ValueError('Slot 3 VAP record table invalid')
    ptr=struct.unpack_from('<'+str(count*3)+'I',blob,base)
    if list(ptr)!=sorted(ptr):raise ValueError('Slot 3 VAP pointers not sorted')
    return base,count,ptr

def match_records(blob,base,ptr,query):
    out=[]
    for p in occurrences(blob,query):
        which=bisect.bisect_right(ptr,p-base)-1
        if which<0:out.append({'offset':p,'message':'outside indexed data'});continue
        start=base+ptr[which]
        stop=blob.find(b'\0',start)
        if stop<0 or stop<p+len(query):
            out.append({'offset':p,'message':'not in primary indexed string'});continue
        out.append({'offset':p,'record':which//3,'column':which%3})
    return out

def read_slot(handle,item,filelen):
    off,decoded,stored,flag=item
    if off+stored>filelen:raise ValueError('IDX entry lies beyond LINKDATA.BIN')
    if flag!=0 or decoded!=stored:raise ValueError('Slot uses unsupported compression')
    handle.seek(off)
    data=handle.read(stored)
    if len(data)!=stored:raise ValueError('Short LINKDATA read')
    return data

def audit(directory:Path,scan_all=False):
    idx=(directory/'LINKDATA.IDX').read_bytes()
    rows=idx_records(idx)
    if len(rows)<4:raise ValueError('Not a DQH1 archive')
    binpath=directory/'LINKDATA.BIN'
    filelen=binpath.stat().st_size
    with binpath.open('rb') as handle:
        system=read_slot(handle,rows[3],filelen)
        base,count,ptr=parse_records(system)
        hits={key:match_records(system,base,ptr,needle) for key,needle in TARGETS.items()}
        report={'scope':'original gameplay dqh1 LINKDATA, never the startup menu',
                'slot_3_sha256':sha(system),'slot_3_bytes':len(system),
                'slot_3_message_records':count,'index_slots':len(rows),
                'labels_in_system_vap':hits,'all_slots_scan_performed':bool(scan_all)}
        if scan_all:
            hit_slots={name:[] for name in TARGETS}
            for i,item in enumerate(rows):
                off,decoded,stored,flag=item
                if flag!=0 or decoded!=stored or stored==0 or stored>128_000_000:continue
                data=system if i==3 else read_slot(handle,item,filelen)
                for name,needle in TARGETS.items():
                    if needle in data:hit_slots[name].append(i)
            report['candidate_uncompressed_slots']=hit_slots
        return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('gameplay_dqh1_directory',type=Path)
    p.add_argument('--scan-all',action='store_true',help='Search every uncompressed slot, may take time')
    p.add_argument('--output',type=Path)
    args=p.parse_args()
    report=audit(args.gameplay_dqh1_directory,args.scan_all)
    encoded=json.dumps(report,indent=2,ensure_ascii=False)+'\n'
    print(encoded,end='')
    if args.output:args.output.write_text(encoded,encoding='utf8')

if __name__=='__main__':main()