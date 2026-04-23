import os
import glob
import uproot
import shutil
import argparse

# ============================================================
# Parse arguments
# ============================================================
parser = argparse.ArgumentParser(description="Apply waveform coincidence selection cuts")
parser.add_argument("--source_dir", required=True, help="Directory containing merged ROOT files")
parser.add_argument("--dest_dir", required=True, help="Destination directory for filtered ROOT files")
args = parser.parse_args()

source_dir = args.source_dir
dest_dir = args.dest_dir

print(f"[INFO] Source directory: {source_dir}")
print(f"[INFO] Destination directory: {dest_dir}")

# ============================================================
# Prepare output directory
# ============================================================
if os.path.exists(dest_dir):
    print(f"[WARNING] Destination already exists, removing: {dest_dir}")
    shutil.rmtree(dest_dir)
os.makedirs(dest_dir, exist_ok=True)
print("[INFO] Created clean destination directory.")

# ============================================================
# Process all ROOT files
# ============================================================
files = glob.glob(os.path.join(source_dir, "*.root"))
print(f"[INFO] Found {len(files)} ROOT files to process.")

selected_count = 0
skipped_count = 0

for file_path in files:
    try:
        with uproot.open(file_path) as f:
            count_ms_ch = 0
            for key in f.keys():
                obj = f[key]
                if "TH1D" in obj.classname and "ms_ch" in key:
                    count_ms_ch += 1

            if count_ms_ch >= 3: #======================================================================
                shutil.copy(file_path, dest_dir)
                selected_count += 1
                print(f"[PASS] {os.path.basename(file_path)} → copied (ms_ch={count_ms_ch})")
            else:
                skipped_count += 1
                print(f"[SKIP] {os.path.basename(file_path)} (ms_ch={count_ms_ch})")

    except Exception as e:
        print(f"[ERROR] Failed to process {file_path}: {e}")

print("====================================================")
print(f"[SUMMARY] Selected files : {selected_count}")
print(f"[SUMMARY] Skipped files  : {skipped_count}")
print(f"[SUMMARY] Output saved in: {dest_dir}")
print("====================================================")
