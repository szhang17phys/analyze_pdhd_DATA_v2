import ROOT
import re
import os

# Directories for input and output files
input_dir = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/t0_rootFiles/data/Decon_event_wvf_extract/"
output_dir = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/t0_rootFiles/data/Decon_wvf_Timing_concidence_merged_dtConstraint/"

# Get list of all ROOT files in the input directory
input_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith(".root")]
print(f"Found {len(input_files)} ROOT files in {input_dir}")

# Regex to extract histogram prefix and channel number
pattern = re.compile(r"(dt[NP]dot\d+ms)_ch(\d+)")

def parse_dt(prefix):
    """Convert a dt prefix string like 'dtNdot0673810ms' or 'dtPdot0027814ms' to a float in ms."""
    if not prefix.startswith("dt"):
        return None
    sign = -1 if prefix[2] == 'N' else 1
    num_str = prefix[6:-2]
    return sign * float("0." + num_str)

def get_opchs(hist_list):
    """Return a sorted list of unique opch numbers from a list of (ch, key) tuples."""
    return sorted({ch for ch, _ in hist_list})

# Process each ROOT file
for input_file in input_files:
    print("\n====================================")
    print("Processing file:", input_file)

    f_in = ROOT.TFile(input_file, "READ")
    if f_in.IsZombie():
        print("Error opening file. Skipping", input_file)
        continue

    keys = [key.GetName() for key in f_in.GetListOfKeys()]

    # Build original groups: dt prefix -> list of (ch, key), with constraint [-0.1, 0.02] ms
    orig_groups = {}
    for key in keys:
        match = pattern.match(key)
        if match:
            prefix, ch = match.groups()
            ch = int(ch)
            dt = parse_dt(prefix)
            if dt is None or not (-0.1 <= dt <= 0.02):
                continue  # Apply constraint here
            orig_groups.setdefault(prefix, []).append((ch, key))

    for prefix, hists in orig_groups.items():
        opchs = get_opchs(hists)
        print(f"{prefix}: {len(hists)} histograms, opchs: {opchs}")

    if not orig_groups:
        print("No valid histograms found in", input_file, ". Skipping.")
        f_in.Close()
        continue

    max_count = max(len(hists) for hists in orig_groups.values())
    max_groups = [(prefix, hists) for prefix, hists in orig_groups.items() if len(hists) == max_count]
    max_groups.sort(key=lambda x: abs(parse_dt(x[0])))

    basename = os.path.basename(input_file)
    match_et = re.search(r"extractDecon_(event\d+_trackID\d+)\.root", basename)
    event_track_part = match_et.group(1) if match_et else "unknown"

    default_max_prefix, default_max_hist_list = max_groups[0]
    default_dt = parse_dt(default_max_prefix)

    merge_candidates = []
    for prefix, hists in orig_groups.items():
        if prefix == default_max_prefix:
            continue
        if len(hists) < max_count:
            other_dt = parse_dt(prefix)
            diff = abs(default_dt - other_dt)
            if diff <= 0.000258:
                merge_candidates.append((prefix, hists, diff))
                print(f"Will merge: {default_max_prefix} and {prefix} (time difference: {diff:.7f} ms)")

    for idx, (sel_prefix, sel_hist_list) in enumerate(max_groups):
        if merge_candidates and idx == 0:
            print(f"Skipping saving default group file for {sel_prefix} because merged file will be created.")
            continue

        opchs = get_opchs(sel_hist_list)
        outfile_name = f"wvfFind_{event_track_part}_opNum{len(sel_hist_list)}.root" if idx == 0 \
            else f"wvfFind_{event_track_part}_opNum{len(sel_hist_list)}_{idx+1}.root"
        output_file = os.path.join(output_dir, outfile_name)
        print(f"Selecting group: {sel_prefix} with {len(sel_hist_list)} histograms, opchs: {opchs}")

        f_out = ROOT.TFile(output_file, "RECREATE")
        canvas_name = "c1_" + os.path.splitext(basename)[0] + f"_{sel_prefix}"
        c1 = ROOT.TCanvas(canvas_name, "Canvas", 1200, 1200)
        c1.Divide(3, 3)

        sel_hist_list.sort()
        total_hist = None

        for i_hist, (ch, hist_name) in enumerate(sel_hist_list):
            hist = f_in.Get(hist_name)
            if not hist:
                continue
            hist.SetDirectory(0)
            f_out.cd()
            hist.Write()
            if total_hist is None:
                total_hist = hist.Clone("total")
                total_hist.SetTitle("Summed Histogram")
            else:
                total_hist.Add(hist)
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

    if merge_candidates:
        merged_hist_list = list(default_max_hist_list)
        for (cand_prefix, cand_hists, diff) in merge_candidates:
            merged_hist_list.extend(cand_hists)
        merged_count = len(merged_hist_list)
        merged_output_file = os.path.join(output_dir, f"wvfFind_{event_track_part}_opNum{max_count}_merged.root")

        f_out_merged = ROOT.TFile(merged_output_file, "RECREATE")
        canvas_name_merged = "c1_" + os.path.splitext(basename)[0] + f"_{default_max_prefix}_merged"
        c1_merged = ROOT.TCanvas(canvas_name_merged, "Canvas", 1200, 1200)
        c1_merged.Divide(3, 3)

        merged_hist_list.sort(key=lambda x: x[0])
        total_hist_merged = None

        for i_hist, (ch, hist_name) in enumerate(merged_hist_list):
            hist = f_in.Get(hist_name)
            if not hist:
                continue
            hist.SetDirectory(0)
            f_out_merged.cd()
            hist.Write()
            if total_hist_merged is None:
                total_hist_merged = hist.Clone("total")
                total_hist_merged.SetTitle("Summed Histogram")
            else:
                total_hist_merged.Add(hist)
            pad_num = ((i_hist % 3) * 3) + (i_hist // 3) + 1
            if pad_num <= 9:
                c1_merged.cd(pad_num)
                hist.Draw()

        if total_hist_merged:
            total_hist_merged.Write()
        f_out_merged.cd()
        c1_merged.Write()
        f_out_merged.Close()
        print(f"Saved merged results to {merged_output_file}")

    f_in.Close()
