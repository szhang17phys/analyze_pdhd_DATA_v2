import os
import ROOT
import argparse


# For results after merge
#input_dir = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/t0_rootFiles/new202510_MC/wvf_merged_20251021"
#output_txt = "./print_wvfCoin_count20251021.txt"


# ============================================================
# SECTION: Parse command-line arguments
# ============================================================
parser = argparse.ArgumentParser(description="Waveform coincidence counting")
parser.add_argument("--input_dir", required=True, help="Input directory (from merged step)")
parser.add_argument("--output_txt", required=True, help="Output text file for counting results")
args = parser.parse_args()

input_dir = args.input_dir
output_txt = args.output_txt

print(f"[INFO] Using input_dir : {input_dir}")
print(f"[INFO] Writing results to: {output_txt}")

# ============================================================
# SECTION: Global ROOT settings
# ============================================================
ROOT.TH1.AddDirectory(False)
ROOT.gROOT.SetBatch(True)
ROOT.gErrorIgnoreLevel = ROOT.kWarning



# List to hold (filename, count) tuples
results = []

# Iterate over all files in the input directory.
for filename in os.listdir(input_dir):
    if filename.endswith(".root"):
        filepath = os.path.join(input_dir, filename)
        root_file = ROOT.TFile(filepath, "READ")
        count = 0
        keys = root_file.GetListOfKeys()
        for key in keys:
            obj = key.ReadObj()
            if obj.InheritsFrom("TH1D") and "ms_ch" in obj.GetName():
                count += 1
        root_file.Close()
        results.append((filename, count))

# Write filename and count to the output file
with open(output_txt, "w") as f:
    for filename, count in results:
        f.write(f"{filename}: {count}\n")

#print(f"Processed {len(results)} files. Results written to {output_txt}.")
