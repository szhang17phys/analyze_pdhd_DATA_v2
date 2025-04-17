import os
import ROOT

#For results without Merge---
#input_dir = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/t0_rootFiles/data_3k/decon_wvf_coincidence"
#output_txt = "./count_wvfCoin_noMerge.txt"

#For results after merge---
input_dir = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/t0_rootFiles/data_3k/decon_wvf_coincidence_merged"
output_txt = "./count_wvfCoin_merged.txt"

# List to hold the counts from each ROOT file.
counts = []

# Iterate over all files in the input directory.
for filename in os.listdir(input_dir):
    if filename.endswith(".root"):
        filepath = os.path.join(input_dir, filename)
        # Open the ROOT file.
        root_file = ROOT.TFile(filepath, "READ")
        count = 0
        # Get all keys (objects) in the file.
        keys = root_file.GetListOfKeys()
        for key in keys:
            obj = key.ReadObj()
            # Check if the object is a TH1D and its name contains "ms_ch"
            if obj.InheritsFrom("TH1D") and "ms_ch" in obj.GetName():
                count += 1
        root_file.Close()
        counts.append(count)

# Write only the count for each file to the output text file, one per line.
with open(output_txt, "w") as f:
    for count in counts:
        f.write(f"{count}\n")

print(f"Processed {len(counts)} files. Results written to {output_txt}.")
