import ROOT
import re
import os
import math

# ============================================================
# SECTION: Directories for input and output files
# ============================================================
input_dir = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/t0_rootFiles/cosmic_28116/decon_event_wvf_extract/"
output_dir = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/t0_rootFiles/cosmic_28116/wvf_merged_28116"


# Channels to ignore completely
exclude_channels = {86, 87, 97, 107, 117, 116, 147, 3, 135}

# Merge tolerance (ms)
MERGE_TOL_MS = 0.000258



# Get list of all ROOT files in the input directory (sorted for reproducibility)
input_files = sorted(
    os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith(".root")
)
print(f"Found {len(input_files)} ROOT files in {input_dir}")

# ============================================================
# SECTION: Helper functions
# ============================================================
pattern = re.compile(r"(dt[NP]dot\d+ms)_ch(\d+)")

def parse_dt(prefix):
    """Convert a dt prefix string to a float value in ms."""
    if not prefix.startswith("dt"):
        return None
    sign = -1 if prefix[2] == 'N' else 1
    num_str = prefix[6:-2]
    return sign * float("0." + num_str)

def get_opchs(hist_list):
    """Return a sorted list of unique opch numbers from a list of (ch, key) tuples."""
    return sorted({ch for ch, _ in hist_list})

def save_group_file(f_in, sel_hist_list, event_track_part, basename, sel_prefix, idx):
    """Save one group (non-merged) to a ROOT file."""
    opchs = get_opchs(sel_hist_list)
    if idx == 0:
        outfile_name = f"wvfFind_{event_track_part}_opNum{len(sel_hist_list)}.root"
    else:
        outfile_name = f"wvfFind_{event_track_part}_opNum{len(sel_hist_list)}_{idx+1}.root"
    output_file = os.path.join(output_dir, outfile_name)
    print(f"Selecting group: {sel_prefix} with {len(sel_hist_list)} histograms, opchs: {opchs}")

    f_out = ROOT.TFile(output_file, "RECREATE")

    canvas_name = "c1_" + os.path.splitext(basename)[0] + f"_{sel_prefix}"
    c1 = ROOT.TCanvas(canvas_name, "Canvas", 1200, 1200)
    n = len(sel_hist_list)
    cols = min(3, n)
    rows = math.ceil(n / cols)
    c1.Divide(cols, rows)

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
        pad_num = i_hist + 1
        if pad_num <= rows * cols:
            c1.cd(pad_num)
            hist.Draw()

    if total_hist:
        total_hist.Write()
    f_out.cd()
    c1.Write()
    f_out.Close()
    print(f"Saved results to {output_file}")

def save_merged_file(f_in, merged_hist_list, event_track_part, basename, prefix, tag="merged"):
    """Save merged histograms to a ROOT file."""
    merged_count = len(merged_hist_list)
    merged_output_file = os.path.join(
        output_dir, f"wvfFind_{event_track_part}_opNum{merged_count}_{tag}.root"
    )

    f_out_merged = ROOT.TFile(merged_output_file, "RECREATE")
    canvas_name_merged = "c1_" + os.path.splitext(basename)[0] + f"_{prefix}_{tag}"
    c1_merged = ROOT.TCanvas(canvas_name_merged, "Canvas", 1200, 1200)

    n = len(merged_hist_list)
    cols = min(3, n)
    rows = math.ceil(n / cols)
    c1_merged.Divide(cols, rows)

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
        pad_num = i_hist + 1
        if pad_num <= rows * cols:
            c1_merged.cd(pad_num)
            hist.Draw()

    if total_hist_merged:
        total_hist_merged.Write()
    f_out_merged.cd()
    c1_merged.Write()
    f_out_merged.Close()
    print(f"Saved merged results to {merged_output_file}")

# ============================================================
# SECTION: Main loop over ROOT files
# ============================================================
for input_file in input_files:
    print("\n====================================")
    print("Processing file:", input_file)

    f_in = ROOT.TFile(input_file, "READ")
    if f_in.IsZombie():
        print("Error opening file. Skipping", input_file)
        continue


    # ============================================================
    # Build histogram groups
    # ============================================================
    keys = [key.GetName() for key in f_in.GetListOfKeys()]
    orig_groups = {}
    for key in keys:
        match = pattern.match(key)
        if match:
            prefix, ch = match.groups()
            ch = int(ch)

            # Skip excluded channels
            if ch in exclude_channels:
                continue

            if prefix not in orig_groups:
                orig_groups[prefix] = []
            orig_groups[prefix].append((ch, key))

    for prefix, hists in orig_groups.items():
        opchs = get_opchs(hists)
        print(f"{prefix}: {len(hists)} histograms, opchs: {opchs}")

    if not orig_groups:
        print("No valid histograms found in", input_file, ". Skipping.")
        f_in.Close()
        continue



    # ============================================================
    # Identify maximum group(s)
    # ============================================================
    max_count = max(len(hists) for hists in orig_groups.values())
    max_groups = [(prefix, hists) for prefix, hists in orig_groups.items() if len(hists) == max_count]
    max_groups.sort(key=lambda x: abs(parse_dt(x[0])))

    # ============================================================
    # Extract event/track info from filename
    # ============================================================
    basename = os.path.basename(input_file)
    match_et = re.search(rf"extractDecon_(event\d+_trackID\d+)\.root", basename)
    event_track_part = match_et.group(1) if match_et else "unknown"




    # ============================================================
    # Normal case: save groups + merged groups
    # ============================================================
    if max_groups and max_count > 1:
        default_max_prefix, default_max_hist_list = max_groups[0]
        default_dt = parse_dt(default_max_prefix)

        # Collect EVERY group within the merge window around default_dt (size doesn't matter)
        merge_candidates = []
        for prefix, hists in orig_groups.items():
            if prefix == default_max_prefix:
                continue
            other_dt = parse_dt(prefix)
            if other_dt is None or default_dt is None:
                continue
            diff = abs(default_dt - other_dt)
            if diff <= MERGE_TOL_MS:
                merge_candidates.append((prefix, hists, diff))
                print(f"Will merge: {default_max_prefix} and {prefix} (time difference: {diff:.7f} ms)")

        # Build the set of prefixes that are covered by the merged output
        merged_prefixes = {default_max_prefix}
        merged_prefixes.update(p for p, _, _ in merge_candidates)

        # Save raw groups ONLY if they are NOT covered by the merged output
        # (If there are no merge candidates, we still save all max groups as before.)
        for idx, (sel_prefix, sel_hist_list) in enumerate(max_groups):
            if sel_prefix in merged_prefixes and merge_candidates:
                print(f"Skipping raw save for {sel_prefix} (covered by merged output).")
                continue
            save_group_file(f_in, sel_hist_list, event_track_part, basename, sel_prefix, idx)

        if merge_candidates:
            # Deduplicate: use dict keyed by (channel, hist_name)
            merged_dict = {(ch, hist_name): (ch, hist_name) for ch, hist_name in default_max_hist_list}
            for cand_prefix, cand_hists, diff in merge_candidates:
                for ch, hist_name in cand_hists:
                    if (ch, hist_name) in merged_dict:
                        print(f"Duplicate found (exact) in normal mode: channel {ch}, hist {hist_name}")
                    elif any(existing_ch == ch for existing_ch, _ in merged_dict.values()):
                        print(f"Channel {ch} already present in merged set with different hist in normal mode: {hist_name}")
                    merged_dict[(ch, hist_name)] = (ch, hist_name)

            merged_hist_list = list(merged_dict.values())
            print(f"Merged {len(merged_hist_list)} unique histograms in normal mode.")
            save_merged_file(f_in, merged_hist_list, event_track_part, basename, default_max_prefix, "merged")



    # ============================================================
    # Fallback case: no max group → median-based merging
    # ============================================================
    else:
        print("No maximum group found, applying fallback median-based merging.")
        dt_groups = sorted(orig_groups.items(), key=lambda x: parse_dt(x[0]))
        median_index = len(dt_groups) // 2
        median_prefix, median_hists = dt_groups[median_index]
        median_dt = parse_dt(median_prefix)

        merge_candidates = []
        for prefix, hists in orig_groups.items():
            if prefix == median_prefix:
                continue
            other_dt = parse_dt(prefix)
            diff = abs(median_dt - other_dt)
            if diff <= MERGE_TOL_MS:
                merge_candidates.append((prefix, hists, diff))
                print(f"Will merge (median mode): {median_prefix} and {prefix} (time difference: {diff:.7f} ms)")

        # Deduplicate: use dict keyed by (channel, hist_name)
        merged_dict = {(ch, hist_name): (ch, hist_name) for ch, hist_name in median_hists}
        for cand_prefix, cand_hists, diff in merge_candidates:
            for ch, hist_name in cand_hists:
                if (ch, hist_name) in merged_dict:
                    print(f"Duplicate found (exact) in fallback mode: channel {ch}, hist {hist_name}")
                elif any(existing_ch == ch for existing_ch, _ in merged_dict.values()):
                    print(f"Channel {ch} already present in merged set with different hist in fallback mode: {hist_name}")
                merged_dict[(ch, hist_name)] = (ch, hist_name)

        merged_hist_list = list(merged_dict.values())
        print(f"Merged {len(merged_hist_list)} unique histograms in fallback mode.")
        save_merged_file(f_in, merged_hist_list, event_track_part, basename, median_prefix, "merged")



    f_in.Close()
