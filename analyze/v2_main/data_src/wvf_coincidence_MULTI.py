import ROOT
import re
import os

# Directories for input and output files
input_dir = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/t0_rootFiles/data/event_wvf_extract/"
output_dir = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/t0_rootFiles/data/wvf_Timing_concidence/"

# Get list of all ROOT files in the input directory
input_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith(".root")]
print(f"Found {len(input_files)} ROOT files in {input_dir}")

# Regex to extract histogram prefix and channel number
pattern = re.compile(r"(dt[NP]dot\d+ms)_ch(\d+)")

def get_opchs(hist_list):
    """Return a sorted list of unique opch numbers from a list of (ch, key) tuples."""
    return sorted({ch for ch, _ in hist_list})

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

    # Build original groups: dictionary mapping histogram prefix -> list of (ch, key)
    orig_groups = {}
    for key in keys:
        match = pattern.match(key)
        if match:
            prefix, ch = match.groups()
            ch = int(ch)
            orig_groups.setdefault(prefix, []).append((ch, key))

    # Print original group details
    for prefix, hists in orig_groups.items():
        opchs = get_opchs(hists)
        print(f"{prefix}: {len(hists)} histograms, opchs: {opchs}")

    if not orig_groups:
        print("No valid histograms found in", input_file, ". Skipping.")
        f_in.Close()
        continue

    # Determine the maximum number of histograms among the original groups
    max_count = max(len(hists) for hists in orig_groups.values())
    # Select all groups that have the maximum count
    max_groups = [(prefix, hists) for prefix, hists in orig_groups.items() if len(hists) == max_count]
    
    # Extract event and trackID from the input filename.
    basename = os.path.basename(input_file)
    match_et = re.search(r"extract_(event\d+_trackID\d+)\.root", basename)
    if match_et:
        event_track_part = match_et.group(1)
    else:
        event_track_part = "unknown"
    
    # Output a separate ROOT file for each maximum group.
    # The first group gets the default name, and additional ones get suffixes _2, _3, etc.
    for idx, (sel_prefix, sel_hist_list) in enumerate(max_groups):
        opchs = get_opchs(sel_hist_list)
        if idx == 0:
            outfile_name = f"wvfFind_{event_track_part}_opNum{len(sel_hist_list)}.root"
        else:
            outfile_name = f"wvfFind_{event_track_part}_opNum{len(sel_hist_list)}_{idx+1}.root"
        output_file = os.path.join(output_dir, outfile_name)
        print(f"Selecting group: {sel_prefix} with {len(sel_hist_list)} histograms, opchs: {opchs}")
    
        # Open output ROOT file
        f_out = ROOT.TFile(output_file, "RECREATE")
    
        # Create a unique canvas (append selected group prefix to canvas name)
        canvas_name = "c1_" + os.path.splitext(basename)[0] + f"_{sel_prefix}"
        c1 = ROOT.TCanvas(canvas_name, "Canvas", 1200, 1200)
        c1.Divide(3, 3)  # 3x3 layout
    
        # Sort histograms by channel number
        sel_hist_list.sort()
        total_hist = None  # To hold the sum of the histograms
    
        # Loop over histograms in the selected group
        for i_hist, (ch, hist_name) in enumerate(sel_hist_list):
            hist = f_in.Get(hist_name)
            if not hist:
                continue
            hist.SetDirectory(0)  # Detach from input file
            f_out.cd()
            hist.Write()
            if total_hist is None:
                total_hist = hist.Clone("total")
                total_hist.SetTitle("Summed Histogram")
            else:
                total_hist.Add(hist)
            # Draw on canvas pad (column-major order for a 3x3 grid)
            pad_num = ((i_hist % 3) * 3) + (i_hist // 3) + 1
            if pad_num <= 9:
                c1.cd(pad_num)
                hist.Draw()
    
        if total_hist:
            total_hist.Write()
        f_out.cd()
        c1.Write()
        f_out.Close()
        print(f"Saved results to {output_file}")
    
    f_in.Close()
