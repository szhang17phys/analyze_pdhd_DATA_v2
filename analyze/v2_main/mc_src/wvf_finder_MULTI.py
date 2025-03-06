import ROOT
import re
import os

# Directories for input and output files
input_dir = "../../../../t0_rootFiles/data/small_test/event_extract/"
output_dir = "../../../../t0_rootFiles/data/small_test/wvf_finder/"

# Get list of all ROOT files in the input directory
input_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith(".root")]
print(f"Found {len(input_files)} ROOT files in {input_dir}")

# Regex to extract histogram prefix and channel number
pattern = re.compile(r"(dt[NP]dot\d+ms)_ch(\d+)")

# Process each ROOT file
for input_file in input_files:
    print("\n====================================")
    print("Processing file:", input_file)
    
    # Open the input ROOT file
    f_in = ROOT.TFile(input_file, "READ")
    if f_in.IsZombie():
        print("Error opening file. Skipping", input_file)
        continue

    # Get list of all keys (histograms)
    keys = [key.GetName() for key in f_in.GetListOfKeys()]

    # Dictionary to store groups of histograms
    hist_groups = {}
    for key in keys:
        match = pattern.match(key)
        if match:
            prefix, ch = match.groups()
            ch = int(ch)  # Convert channel to integer for sorting
            if prefix not in hist_groups:
                hist_groups[prefix] = []
            hist_groups[prefix].append((ch, key))

    # Print histogram counts and related channel numbers per group
    for prefix, hists in hist_groups.items():
        # Extract and sort channel numbers from the histogram list
        channels = sorted(ch for ch, _ in hists)
        print(f"{prefix}: {len(hists)} histograms, opchs: {channels}")


    # Find the group with the most histograms
    max_group = max(hist_groups.items(), key=lambda x: len(x[1]), default=None)
    if not max_group:
        print("No valid histograms found in", input_file, ". Skipping.")
        f_in.Close()
        continue

    max_prefix, max_hist_list = max_group
    num_waveforms = len(max_hist_list)
    print(f"Selecting group: {max_prefix} with {num_waveforms} histograms.")

    # Extract event and track parts from the input filename.
    # Expected filename: "extract_eventXXXX_trackIDY.root"
    basename = os.path.basename(input_file)
    match_et = re.search(r"extract_(event\d+_trackID\d+)\.root", basename)
    if match_et:
        event_track_part = match_et.group(1)
    else:
        event_track_part = "unknown"

    # Build the output file name.
    output_file = os.path.join(output_dir, f"wvfFind_{event_track_part}_opNum{num_waveforms}.root")

    # Open output ROOT file
    f_out = ROOT.TFile(output_file, "RECREATE")

    # Create a unique canvas for this file (use the basename in the canvas name)
    canvas_name = "c1_" + os.path.splitext(basename)[0]
    c1 = ROOT.TCanvas(canvas_name, "Canvas", 1200, 1200)
    c1.Divide(3, 3)  # 3x3 layout

    # Sort histograms by channel number
    max_hist_list.sort()

    # Sum histogram (to hold the sum of all histograms in the group)
    total_hist = None

    # Loop over histograms in the selected group
    for i, (ch, hist_name) in enumerate(max_hist_list):
        hist = f_in.Get(hist_name)
        if not hist:
            continue

        hist.SetDirectory(0)  # Detach histogram from input file
        f_out.cd()
        hist.Write()

        # Sum histograms
        if total_hist is None:
            total_hist = hist.Clone("total")
            total_hist.SetTitle("Summed Histogram")
        else:
            total_hist.Add(hist)

        # Compute pad number in column-major order.
        # For a 3x3 grid, pad_num = ((i % 3) * 3) + (i // 3) + 1
        pad_num = ((i % 3) * 3) + (i // 3) + 1
        if pad_num <= 9:
            c1.cd(pad_num)
            hist.Draw()

    # Write total histogram and canvas to output file
    if total_hist:
        total_hist.Write()

    f_out.cd()
    c1.Write()

    # Close the files
    f_out.Close()
    f_in.Close()

    print(f"Saved results to {output_file}")
