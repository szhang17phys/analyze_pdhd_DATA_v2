import ROOT
import re
import os

# Input and output filenames
input_file = "./extract_event4042_trackID2.root"
output_file = "./wvfFinder_event4042_trackID2.root"

# Open the input ROOT file
f_in = ROOT.TFile(input_file, "READ")

# Get list of all keys (histograms)
keys = [key.GetName() for key in f_in.GetListOfKeys()]

# Dictionary to store groups of histograms
hist_groups = {}

# Regex to extract the prefix (supports both dtNdot and dtPdot)
pattern = re.compile(r"(dt[NP]dot\d+us)_ch(\d+)")

for key in keys:
    match = pattern.match(key)
    if match:
        prefix, ch = match.groups()
        ch = int(ch)  # Convert channel to integer for sorting
        if prefix not in hist_groups:
            hist_groups[prefix] = []
        hist_groups[prefix].append((ch, key))  # Store channel and name

# Count and display the number of histograms per group
for prefix, hists in hist_groups.items():
    print(f"{prefix}: {len(hists)} histograms")

# Find the group with the most histograms
max_group = max(hist_groups.items(), key=lambda x: len(x[1]), default=None)

if not max_group:
    print("No valid histograms found. Exiting.")
    f_in.Close()
    exit()

max_prefix, max_hist_list = max_group

print(f"\nSelecting group: {max_prefix} with {len(max_hist_list)} histograms.")

# Open output ROOT file
f_out = ROOT.TFile(output_file, "RECREATE")

# Create canvas
c1 = ROOT.TCanvas("c1", "Canvas", 1200, 1200)
c1.Divide(3, 3)  # 3x3 layout

# Sort histograms by channel number
max_hist_list.sort()

# Sum histogram
total_hist = None

# Copy histograms to the new file and draw them
for i, (ch, hist_name) in enumerate(max_hist_list):
    hist = f_in.Get(hist_name)
    if not hist:
        continue

    hist.SetDirectory(0)  # Detach from input file
    f_out.cd()
    hist.Write()

    # Sum histograms
    if total_hist is None:
        total_hist = hist.Clone("total")
        total_hist.SetTitle("Summed Histogram")
    else:
        total_hist.Add(hist)

    # Draw on canvas
    pad_num = i + 1
    if pad_num <= 9:
        c1.cd(pad_num)
        hist.Draw()

# Write total histogram and canvas to output file
if total_hist:
    total_hist.Write()

f_out.cd()
c1.Write()

# Close files
f_out.Close()
f_in.Close()

print(f"Saved results to {output_file}")
