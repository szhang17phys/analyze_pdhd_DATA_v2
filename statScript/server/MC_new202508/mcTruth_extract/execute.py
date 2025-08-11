#!/usr/bin/env python3
import os
import re
import subprocess
from time import sleep
from pathlib import Path

# --- config ---
input_dir  = Path("/pnfs/dune/scratch/users/szh2/MC_pdhd_Michel/my_production_20250804")
output_dir = Path("/exp/dune/data/users/szh2/running_results/MC_PDHD_list/mcTruth_extract/new20250804_MC")
fcl        = "pdhd_Truechecks.fcl"
timeout_s  = 1800   # 30 min per file; tune as needed
retries    = 2      # total attempts
backoff_s  = 10     # seconds between retries
# --------------

output_dir.mkdir(parents=True, exist_ok=True)

def basename_from_reco(fname: str) -> str:
    m = re.search(r"reco_(.*)\.root$", fname)
    return m.group(1) if m else os.path.splitext(fname)[0]

root_files = sorted([p for p in input_dir.iterdir() if p.suffix == ".root"])
print(f"[INFO] Found {len(root_files)} ROOT files.")

for idx, rf in enumerate(root_files, 1):
    base = basename_from_reco(rf.name)
    out_txt = output_dir / f"{base}.txt"

    if out_txt.exists() and out_txt.stat().st_size > 0:
        print(f"[{idx}/{len(root_files)}] SKIP {rf.name} (already done)")
        continue

    cmd = ["lar", "-c", fcl, "-s", str(rf)]
    attempt = 0
    while attempt < retries:
        attempt += 1
        print(f"[{idx}/{len(root_files)}] RUN {rf.name} (try {attempt}/{retries})")
        try:
            with open(out_txt, "w") as out:
                subprocess.run(cmd, stdout=out, stderr=subprocess.STDOUT, text=True,
                               timeout=timeout_s, check=False)
            print(f"[OK] {rf.name} -> {out_txt}")
            break
        except subprocess.TimeoutExpired:
            print(f"[TIMEOUT] {rf.name} (> {timeout_s}s)")
            if attempt < retries:
                print(f"[RETRY] sleeping {backoff_s}s...")
                sleep(backoff_s)
            else:
                print(f"[FAIL] giving up on {rf.name}")
