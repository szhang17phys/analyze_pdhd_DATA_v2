import os
import re
import glob
from collections import Counter

import ROOT


# ==========================================================
# Configuration
# ==========================================================
input_dir = "/Volumes/ssd_zhang/thesis_michel/server_processing/t0_rootFiles/new20251010s/wvf_merged_20251045"
output_txt = "opch_count_20251045.txt"





root_files = glob.glob(os.path.join(input_dir, "*.root"))

# Regex to extract channel number
pattern = re.compile(r"_ch(\d+)")

# Global accumulator
channel_counter = Counter()


# ==========================================================
# Loop over all files and accumulate
# ==========================================================
print(f"[INFO] Processing {len(root_files)} files...")

for i, file_path in enumerate(root_files, 1):

    if i % 200 == 0:
        print(f"[INFO] {i}/{len(root_files)}")

    f = ROOT.TFile.Open(file_path)

    if not f or f.IsZombie():
        print(f"[WARN] Bad file: {file_path}")
        continue

    for key in f.GetListOfKeys():

        if key.GetClassName() != "TH1D":
            continue

        name = key.GetName()

        if name == "total":
            continue

        match = pattern.search(name)
        if match:
            ch = int(match.group(1))
            channel_counter[ch] += 1   # <-- GLOBAL accumulation

    f.Close()


# ==========================================================
# Output
# ==========================================================
with open(output_txt, "w") as fout:
    fout.write("OpCh\tCount\n")

    for ch in sorted(channel_counter):
        fout.write(f"{ch}\t{channel_counter[ch]}\n")


print("\n[DONE] Global accumulation finished.")
print(f"[OUTPUT] {output_txt}")