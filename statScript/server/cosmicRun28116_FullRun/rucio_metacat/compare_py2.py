#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
from collections import defaultdict

# -------------------------------------------------------------------
# User paths
# -------------------------------------------------------------------
txt_file = "rucio_paths_Full.txt"
local_folder = "/pnfs/dune/scratch/users/szh2/pdhd_DATA_Michel/cosmicRun_28116/michelt0_6k_files"
output_missing = "missing_paths.txt"
output_dups = "duplicate.txt"

# Regex pattern for extracting core identifier
pattern = re.compile(r"(run\d+_\d+_dataflow\d+_datawriter_0_\d{8}T\d{6})")

# -------------------------------------------------------------------
# 1. Extract all identifiers and record duplicates
# -------------------------------------------------------------------
id_to_fullpath = {}
txt_ids = set()
duplicates = defaultdict(list)

with open(txt_file, "r") as f:
    for lineno, line in enumerate(f, start=1):
        line = line.strip()
        m = pattern.search(line)
        if not m:
            print("WARNING: No match in line {}: {}".format(lineno, line))
            continue

        key = m.group(1)

        if key in id_to_fullpath:
            duplicates[key].append(line)
        else:
            id_to_fullpath[key] = line

        txt_ids.add(key)

print("Loaded {} unique IDs from TXT file.".format(len(txt_ids)))
print("Found {} duplicated ID entries.".format(len(duplicates)))

# -------------------------------------------------------------------
# 2. Extract identifiers from local ROOT files
# -------------------------------------------------------------------
local_ids = set()

for fname in os.listdir(local_folder):
    m = pattern.search(fname)
    if m:
        local_ids.add(m.group(1))

print("Found {} unique IDs in local folder.".format(len(local_ids)))

# -------------------------------------------------------------------
# 3. Compare sets
# -------------------------------------------------------------------
missing = sorted(txt_ids - local_ids)
print("Total missing: {}".format(len(missing)))

# -------------------------------------------------------------------
# 4. Save missing paths
# -------------------------------------------------------------------
with open(output_missing, "w") as f:
    for key in missing:
        f.write(id_to_fullpath[key] + "\n")

print("Missing paths saved to: {}".format(output_missing))

# -------------------------------------------------------------------
# 5. Save duplicate IDs and their lines
# -------------------------------------------------------------------
if len(duplicates) > 0:
    with open(output_dups, "w") as f:
        for key, lines in duplicates.items():
            f.write("==== DUPLICATE ID: {} ====\n".format(key))
            f.write("Original: {}\n".format(id_to_fullpath[key]))
            for dup in lines:
                f.write("Duplicate: {}\n".format(dup))
            f.write("\n")

    print("Duplicate IDs saved to: {}".format(output_dups))
else:
    print("No duplicate IDs found.")
