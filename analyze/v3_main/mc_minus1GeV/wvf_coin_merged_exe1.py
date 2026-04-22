import ROOT
import re
import os
import math
import gc
import argparse


# ============================================================
# SECTION: Parse input arguments
# ============================================================
parser = argparse.ArgumentParser(
    description="Merge waveform ROOT histograms from input directory and write results to output directory."
)
parser.add_argument(
    "--input_dir",
    required=True,
    help="Path to the input directory containing extracted waveform ROOT files."
)
parser.add_argument(
    "--output_dir",
    required=True,
    help="Path to the output directory for merged ROOT files."
)

args = parser.parse_args()


# ============================================================
# SECTION: Global ROOT memory settings
# ============================================================
ROOT.TH1.AddDirectory(False)
ROOT.gROOT.SetBatch(True)
ROOT.gErrorIgnoreLevel = ROOT.kWarning

# ============================================================
# SECTION: Directories for input and output files
# ============================================================
#input_dir = "/Volumes/ssd_zhang/thesis_michel/server_processing/t0_rootFiles/beam28891_new202602/decon_event_wvf_extract/"
#output_dir = "/Volumes/ssd_zhang/thesis_michel/server_processing/t0_rootFiles/beam28891_new202602/wvf_merged/"

input_dir = args.input_dir
output_dir = args.output_dir

exclude_channels = {86, 87, 97, 107, 117, 116, 147, 3, 135}
MERGE_TOL_MS = 0.000258

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
    """Return sorted list of unique optical channels."""
    return sorted({ch for ch, _ in hist_list})

def clear_root_memory():
    """Clear ROOT's internal object lists."""
    ROOT.gDirectory.Clear()
    ROOT.gROOT.GetListOfCanvases().Delete()
    ROOT.gROOT.GetListOfFiles().Delete()
    gc.collect()

def save_group_file(f_in, sel_hist_list, event_track_part, basename, sel_prefix, idx):
    """Save one group to a ROOT file."""
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
    del c1, f_out, total_hist
    gc.collect()
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
    del c1_merged, f_out_merged, total_hist_merged
    gc.collect()
    print(f"Saved merged results to {merged_output_file}")

# ============================================================
# SECTION: Main loop over ROOT files
# ============================================================
input_files = sorted(
    os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith(".root")
)
print(f"Found {len(input_files)} ROOT files in {input_dir}")

for idx, input_file in enumerate(input_files):
    print("\n====================================")
    print(f"[{idx+1}/{len(input_files)}] Processing file: {input_file}")

    f_in = ROOT.TFile.Open(input_file, "READ")
    if not f_in or f_in.IsZombie():
        print("Error opening file. Skipping", input_file)
        continue

    # ============================================================
    # Build histogram groups
    # ============================================================
    # --- Collect only latest-cycle histograms (avoid ;1, ;2 duplicates) ---
    keys = []
    seen_names = set()
    for key in f_in.GetListOfKeys():
        name = key.GetName()
        # Skip duplicate cycles of same histogram name
        if name in seen_names:
            continue
        latest_key = f_in.GetKey(name)  # ROOT returns latest cycle automatically
        if latest_key:
            keys.append(latest_key.GetName())
            seen_names.add(name)

    # --- Group by dt prefix and channel number as before ---
    orig_groups = {}
    for key in keys:
        match = pattern.match(key)
        if match:
            prefix, ch = match.groups()
            ch = int(ch)
            if ch in exclude_channels:
                continue
            if prefix not in orig_groups:
                orig_groups[prefix] = []
            orig_groups[prefix].append((ch, key))

    if not orig_groups:
        print("No valid histograms found in", input_file)
        f_in.Close()
        del f_in
        clear_root_memory()
        continue

    for prefix, hists in orig_groups.items():
        opchs = get_opchs(hists)
        print(f"{prefix}: {len(hists)} histograms, opchs: {opchs}")


    # ============================================================
    # Identify maximum group(s)
    # ============================================================
    max_count = max(len(hists) for hists in orig_groups.values())
    max_groups = [(prefix, hists) for prefix, hists in orig_groups.items() if len(hists) == max_count]
    max_groups.sort(key=lambda x: abs(parse_dt(x[0])))

    basename = os.path.basename(input_file)

    # Extract fileID + event + trackID
    m = re.search(r"(file\d+_\d+_\d+_\d+T\d+Z)_.*_(event\d+_trackID\d+)", basename)

    if m:
        fileID_part = m.group(1)
        event_track_part = m.group(2)
        full_id_part = f"{fileID_part}_{event_track_part}"
    else:
        full_id_part = "unknown"


    # ============================================================
    # Normal case
    # ============================================================
    if max_groups and max_count > 1:
        default_max_prefix, default_max_hist_list = max_groups[0]
        default_dt = parse_dt(default_max_prefix)

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
                print(f"Will merge: {default_max_prefix} and {prefix} (Δt={diff:.7f} ms)")

        merged_prefixes = {default_max_prefix}
        merged_prefixes.update(p for p, _, _ in merge_candidates)

        for idxg, (sel_prefix, sel_hist_list) in enumerate(max_groups):
            if sel_prefix in merged_prefixes and merge_candidates:
                print(f"Skipping raw save for {sel_prefix} (covered by merged output).")
                continue
            save_group_file(f_in, sel_hist_list, full_id_part, basename, sel_prefix, idxg)

        if merge_candidates:
            merged_dict = {(ch, hist_name): (ch, hist_name) for ch, hist_name in default_max_hist_list}
            for cand_prefix, cand_hists, diff in sorted(merge_candidates, key=lambda x: abs(parse_dt(x[0]))):
                for ch, hist_name in cand_hists:
                    if (ch, hist_name) in merged_dict:
                        print(f"Duplicate found (exact): channel {ch}, hist {hist_name}")
                    elif any(existing_ch == ch for existing_ch, _ in merged_dict.values()):
                        print(f"Channel {ch} already present (different hist): {hist_name}")
                    merged_dict[(ch, hist_name)] = (ch, hist_name)
            merged_hist_list = list(merged_dict.values())
            print(f"Merged {len(merged_hist_list)} unique histograms (normal mode).")
            save_merged_file(f_in, merged_hist_list, full_id_part, basename, default_max_prefix, "merged")

    # ============================================================
    # Fallback case
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
                print(f"Will merge (median mode): {median_prefix} and {prefix} (Δt={diff:.7f} ms)")

        merged_dict = {(ch, hist_name): (ch, hist_name) for ch, hist_name in median_hists}
        for cand_prefix, cand_hists, diff in sorted(merge_candidates, key=lambda x: abs(parse_dt(x[0]))):
            for ch, hist_name in cand_hists:
                if (ch, hist_name) in merged_dict:
                    print(f"Duplicate found (fallback): {hist_name}")
                elif any(existing_ch == ch for existing_ch, _ in merged_dict.values()):
                    print(f"Channel {ch} already present (fallback): {hist_name}")
                merged_dict[(ch, hist_name)] = (ch, hist_name)

        merged_hist_list = list(merged_dict.values())
        print(f"Merged {len(merged_hist_list)} unique histograms (fallback mode).")
        save_merged_file(f_in, merged_hist_list, full_id_part, basename, median_prefix, "merged")

    # ============================================================
    # Cleanup
    # ============================================================
    f_in.Close()
    del f_in
    clear_root_memory()
    print(f"✅ Finished file {idx+1}/{len(input_files)}")

print("\n🎉 All files processed successfully.")
