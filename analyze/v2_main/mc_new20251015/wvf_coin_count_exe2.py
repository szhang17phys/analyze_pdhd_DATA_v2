import os
import ROOT

# For results after merge
input_dir = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/t0_rootFiles/new202510_MC/wvf_merged_20251015"
output_txt = "./print_wvfCoin_count20251015.txt"

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
