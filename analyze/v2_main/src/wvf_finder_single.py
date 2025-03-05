import ROOT
import re
import os

# Input filename (example)
input_file = "../../../../t0_rootFiles/small_test/event_extract/extract_event85604_trackID7.root"

# Open the input ROOT file
f_in = ROOT.TFile(input_file, "READ")

# Get list of all keys (histograms)
keys = [key.GetName() for key in f_in.GetListOfKeys()]

# Dictionary to store groups of histograms
hist_groups = {}

# Regex to extract the prefix (supports both dtNdot and dtPdot)
pattern = re.compile(r"(dt[NP]dot\d+ms)_ch(\d+)")

for key in keys:
    match = pattern.match(key)
    if match:
        prefix, ch = match.groups()
        ch = int(ch)  # Convert channel to integer for sorting
        if prefix not in hist_groups:
            hist_groups[prefix] = []
        hist_groups[prefix].append((ch, key))  # Store channel and name

# Print histogram counts and related channel numbers per group
for prefix, hists in hist_groups.items():
    # Extract and sort channel numbers from the histogram list
    channels = sorted(ch for ch, _ in hists)
    print(f"{prefix}: {len(hists)} histograms, opchs: {channels}")

# Find the group with the most histograms
max_group = max(hist_groups.items(), key=lambda x: len(x[1]), default=None)

if not max_group:
    print("No valid histograms found. Exiting.")
    f_in.Close()
    exit()

max_prefix, max_hist_list = max_group
num_waveforms = len(max_hist_list)
print(f"\nSelecting group: {max_prefix} with {num_waveforms} histograms.")


# Extract the event and track parts from the input filename.
# This regex expects the input filename to be like "extract_event85604_trackID7.root"
basename = os.path.basename(input_file)
match_et = re.search(r"extract_(event\d+_trackID\d+)\.root", basename)
if match_et:
    event_track_part = match_et.group(1)
else:
    event_track_part = "unknown"

# Build the output file name.
# The output file will be placed in the sibling folder "wvf_finder" relative to the input file's parent.
output_dir = "../../../../t0_rootFiles/small_test/wvf_finder/"
output_file = os.path.join(output_dir, f"wvfFind_{event_track_part}_opNum{num_waveforms}.root")

# Open output ROOT file
f_out = ROOT.TFile(output_file, "RECREATE")

# Create canvas
c1 = ROOT.TCanvas("c1", "Canvas", 1200, 1200)
c1.Divide(3, 3)  # 3x3 layout

# Sort histograms by channel number
max_hist_list.sort()

# Sum histogram (to hold the sum of all histograms in the group)
total_hist = None

# Copy histograms to the new file and draw them on canvas
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

    # Draw histogram on canvas (first 9 pads)
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
