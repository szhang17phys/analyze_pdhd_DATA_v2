import re
from collections import defaultdict

# --- Define the pattern ---
# Ex: michelt0_MC_decon_20240411T230901Z_192205_038498.root
#pattern = re.compile(r"(_\d{2,6}_dataflow\d{1,2}_datawriter_0_\d{8}T\d{6})")
pattern = re.compile(r"(_\d{8}T\d{6}Z_\d{3,7}_\d{3,7})")

# =====================
# --- Process part1.txt ---
# =====================
with open("part1.txt", "r") as f1:
    part1_lines = f1.readlines()

part1_key_to_lines = defaultdict(list)
for line in part1_lines:
    match = pattern.search(line)
    if match:
        key = match.group(1)
        part1_key_to_lines[key].append(line.strip())

# ===============================
# --- Process rucio_paths_Full.txt ---
# ===============================
with open("rucio_2k_FNAL.txt", "r") as f2:
    list_lines = f2.readlines()

rucio_key_to_lines = defaultdict(list)
for line in list_lines:
    match = pattern.search(line)
    if match:
        key = match.group(1)
        rucio_key_to_lines[key].append(line.strip())

# ==========================
# --- Find unmatched lines ---
# ==========================
part1_keys = set(part1_key_to_lines.keys())
rucio_keys = set(rucio_key_to_lines.keys())

unmatched_lines = []
for line in list_lines:
    match = pattern.search(line)
    if match:
        if match.group(1) not in part1_keys:
            unmatched_lines.append(line.strip())
    else:
        unmatched_lines.append(line.strip())  # No pattern match at all

# =====================================
# --- Print duplicated keys in rucio ---
# =====================================
print("\n===== Keys with multiple corresponding lines in rucio_paths_Full.txt =====")
for key, lines in rucio_key_to_lines.items():
    if len(lines) > 1:
        print(f"\nKey: {key}")
        for l in lines:
            print(f"  {l}")

# ====================================
# --- Print duplicated keys in part1 ---
# ====================================
print("\n===== Keys with multiple corresponding lines in part1.txt =====")
for key, lines in part1_key_to_lines.items():
    if len(lines) > 1:
        print(f"\nKey: {key}")
        for l in lines:
            print(f"  {l}")

# ==================================
# --- Print unmatched lines in rucio ---
# ==================================
print("\n===== Lines in rucio_paths_Full.txt without correspondence in part1.txt =====")
for line in unmatched_lines:
    print(line)

# ===================
# --- Print summary ---
# ===================
print("\n===== Summary =====")
print(f"Total lines in part1.txt: {len(part1_lines)}")
print(f"Total lines in rucio_paths_Full.txt: {len(list_lines)}")
print(f"Total unique keys in part1.txt: {len(part1_keys)}")
print(f"Total unique keys in rucio_paths_Full.txt: {len(rucio_keys)}")
print(f"Total unmatched lines in rucio_paths_Full.txt: {len(unmatched_lines)}")

num_duplicated_in_rucio = sum(1 for v in rucio_key_to_lines.values() if len(v) > 1)
num_duplicated_in_part1 = sum(1 for v in part1_key_to_lines.values() if len(v) > 1)

print(f"Total keys with duplicated lines in rucio_paths_Full.txt: {num_duplicated_in_rucio}")
print(f"Total keys with duplicated lines in part1.txt: {num_duplicated_in_part1}")
