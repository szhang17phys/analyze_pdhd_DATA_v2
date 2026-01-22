import os
import ROOT

# For results after merge
input_dir = "/Volumes/ssd_zhang/thesis_michel/server_processing/t0_rootFiles/cosmicData_new202512/27980/wvf_merged"
output_txt = "./print_wvfCoin_count20260121.txt"

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
