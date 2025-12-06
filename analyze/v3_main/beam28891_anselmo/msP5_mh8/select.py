import os
import re
import shutil

# --- Directories ---
src_dir = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/t0_rootFiles/data_28891_FullRun/decon_wvf_coincidence_applyCut"

txt_path = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/analyze_pdhd_DATA_v2/statScript/local/beamRun28891_FullRun/applyCut_print/filtered_fullRun_print.txt"

dest_dir = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/t0_rootFiles/data_28891_FullRun/applyCut_MSp5MH8_anselmo"

os.makedirs(dest_dir, exist_ok=True)

# --- Read and cache text file ---
with open(txt_path, "r") as f:
    text = f.read()

# --- Updated regex: also capture Michel hits ---
pattern = re.compile(
    r"Michel score:\s*([0-9.]+).*?Michel hits:\s*(\d+).*?"
    r"Run:\s*(\d+),\s*Event:\s*(\d+),\s*TrackID:\s*(\d+)",
    re.S,
)

# --- Store score + hits + run/event/track ---
michel_entries = [
    {"score": float(s), "hits": int(h), "run": int(r), "event": int(e), "track": int(t)}
    for s, h, r, e, t in pattern.findall(text)
]

# --- Helper: check if (event, track) matches ---
def find_entry(event, track):
    for entry in michel_entries:
        if entry["event"] == event and entry["track"] == track:
            return entry
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

    entry = find_entry(event, track)
    if entry is not None:
        score = entry["score"]
        hits = entry["hits"]
        print(f"{fname:60s}  Event={event:6d}, Track={track:4d}, "
              f"Score={score:.3f}, Hits={hits:d}")
        matched_count += 1

        #==============================================
        # NEW selection: score > 0.6 AND hits > 8
        #==============================================
        if score > 0.5 and hits > 8:
            shutil.copy2(os.path.join(src_dir, fname), dest_dir)
            copied_count += 1

print(f"\nTotal matched files: {matched_count}")
print(f"Copied high-score & high-hit files: {copied_count}")
