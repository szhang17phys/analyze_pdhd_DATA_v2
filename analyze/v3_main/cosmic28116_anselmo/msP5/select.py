import os
import re
import shutil

# --- Directories ---
src_dir = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/t0_rootFiles/cosmic_28116/wvf_merged_applyCut_new20251029"

txt_path = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/analyze_pdhd_DATA_v2/statScript/local/cosmicRun28116_FullRun/applyCut_print/filtered_fullRun_print.txt"

dest_dir = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/t0_rootFiles/cosmic_28116/applyCut_MSp5_anselmo"

os.makedirs(dest_dir, exist_ok=True)

# --- Read and cache text file ---
with open(txt_path, "r") as f:
    text = f.read()

# --- Find all Michel candidate blocks ---
pattern = re.compile(
    r"Michel score:\s*([0-9.]+).*?Run:\s*(\d+),\s*Event:\s*(\d+),\s*TrackID:\s*(\d+)",
    re.S,
)
michel_entries = [
    {"score": float(s), "run": int(r), "event": int(e), "track": int(t)}
    for s, r, e, t in pattern.findall(text)
]

# --- Helper: check if (event, track) matches ---
def find_score(event, track):
    for entry in michel_entries:
        if entry["event"] == event and entry["track"] == track:
            return entry["score"]
    return None

# --- Parse filenames ---
file_pattern = re.compile(r"event(\d+)_trackID(\d+)")
matched_count = 0
copied_count = 0

for fname in os.listdir(src_dir):
    if not fname.endswith(".root"):
        continue
    m = file_pattern.search(fname)
    if not m:
        continue
    event = int(m.group(1))
    track = int(m.group(2))

    score = find_score(event, track)
    if score is not None:
        print(f"{fname:60s}  Event={event:6d}, Track={track:4d}, Score={score:.3f}")
        matched_count += 1

        #==============================================
        if score > 0.5:
        #==============================================

            shutil.copy2(os.path.join(src_dir, fname), dest_dir)
            copied_count += 1

print(f"\nTotal matched files: {matched_count}")
print(f"Copied high-score files (>0.5): {copied_count}")
