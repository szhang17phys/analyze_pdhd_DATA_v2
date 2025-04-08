import os
import glob
import uproot
import shutil

# Define source and destination directories
source_dir = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/t0_rootFiles/data/Decon_wvf_Timing_concidence_merged_dtConstraint"
dest_dir = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/t0_rootFiles/data/Decon_wvfNumCut5_merged_dtConstraint"

# Create destination directory if it doesn't exist
if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)

# Loop over all ROOT files in the source directory
for file_path in glob.glob(os.path.join(source_dir, "*.root")):
    print(f"Processing file: {file_path}")
    try:
        with uproot.open(file_path) as f:
            count_ms_ch = 0
            # Iterate over all keys (objects) in the ROOT file
            for key in f.keys():
                obj = f[key]
                # Check if the object is a TH1D histogram and if its name contains "ms_ch"
                if "TH1D" in obj.classname and "ms_ch" in key:
                    count_ms_ch += 1

            print(f"  Found {count_ms_ch} TH1D histograms containing 'ms_ch'.")
            # If more than 4 such histograms, copy the file to the destination directory
            if count_ms_ch > 4:
                shutil.copy(file_path, dest_dir)
                print("  File copied to destination.")
    except Exception as e:
        print(f"  Error processing file {file_path}: {e}")

