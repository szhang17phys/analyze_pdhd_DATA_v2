#!/usr/bin/env python3
import os
import re
import glob
import shutil
from pathlib import Path


# ============================================================
# =========================== CONFIG =========================
# ============================================================

CONFIG = {
    # ---- Source ROOT files directory ----
    "SRC_DIR": Path(
        "/Volumes/ssd_zhang/thesis_michel/server_processing/t0_rootFiles/beam28891_new202602/wvf_merged_applyCut_thre3"
    ),

    # ---- Destination directory (copy files OUTSIDE [A,B] here) ----
    "DST_DIR": Path(
        "/Volumes/ssd_zhang/thesis_michel/server_processing/t0_rootFiles/beam28891_new202602/wvf_applyCut_removeBeam"
    ),

    # ---- Cut window [A, B] on Pandora_T0[ms] ----
    "A": -0.12,
    "B": -0.03,

    # ---- Log files (full paths) ----
    "LOG_FILES": [
        Path(
            "/Volumes/ssd_zhang/thesis_michel/server_processing/statScript_local/event_wvf_extract/beam28891/print_part1.log"
        ),
        Path(
            "/Volumes/ssd_zhang/thesis_michel/server_processing/statScript_local/event_wvf_extract/beam28891/print_part2.log"
        ),
        Path(
            "/Volumes/ssd_zhang/thesis_michel/server_processing/statScript_local/event_wvf_extract/beam28891/print_part3.log"
        ),
    ],

    # ---- Search this many lines after "Run: ..., Event: ..., TrackID: ..." for Pandora_T0 ----
    "SEARCH_WINDOW": 4,

    # ---- If True: no copying, only print actions ----
    "DRY_RUN": False,
}


# ============================================================
# ===================== CORE FUNCTIONS =======================
# ============================================================

def build_pandora_index(log_paths, search_window):
    """
    Build dict:
        (event:int, trackID:int) -> Pandora_T0[ms]:float
    We detect:
      Run: 28891,  Event: 82,  TrackID: 42
    then search forward within `search_window` lines for:
      Pandora_T0[ms]: -2.4226
    """
    key_re = re.compile(r"Run:\s*\d+,\s*Event:\s*(\d+),\s*TrackID:\s*(\d+)")
    pandora_re = re.compile(r"Pandora_T0\[ms\]:\s*([+-]?\d+(?:\.\d+)?)")

    index = {}

    for log_path in log_paths:
        if not log_path.exists():
            print(f"[ERROR] Log file not found: {log_path}")
            continue

        print(f"[INFO] Reading {log_path}")
        with log_path.open("r", errors="replace") as f:
            pending_key = None
            remaining = 0

            for line in f:
                if pending_key is None:
                    m = key_re.search(line)
                    if m:
                        event = int(m.group(1))
                        trackid = int(m.group(2))
                        pending_key = (event, trackid)
                        remaining = search_window
                    continue

                mp = pandora_re.search(line)
                if mp:
                    index[pending_key] = float(mp.group(1))
                    pending_key = None
                    remaining = 0
                    continue

                remaining -= 1
                if remaining <= 0:
                    pending_key = None

    return index


def extract_event_trackid_from_filename(fname):
    """
    Parse event and trackID from filenames like:
      wvfFind_event99947_trackID2_opNum8.root
      wvfFind_event99843_trackID17_opNum4_merged.root
      wvfFind_event99932_trackID0_opNum8_2.root
    """
    base = os.path.basename(fname)
    m = re.search(r"wvfFind_event(\d+)_trackID(\d+)_", base)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2))


# ============================================================
# =========================== MAIN ===========================
# ============================================================

def main():
    src_dir = CONFIG["SRC_DIR"]
    dst_dir = CONFIG["DST_DIR"]
    log_files = CONFIG["LOG_FILES"]
    a = float(CONFIG["A"])
    b = float(CONFIG["B"])
    search_window = int(CONFIG["SEARCH_WINDOW"])
    dry_run = bool(CONFIG["DRY_RUN"])

    print("============================================================")
    print("CONFIG SUMMARY")
    print("============================================================")
    print(f"SRC_DIR        : {src_dir}")
    print(f"DST_DIR        : {dst_dir}")
    print(f"Cut window [A,B]: [{a}, {b}]")
    print(f"SEARCH_WINDOW  : {search_window}")
    print(f"DRY_RUN        : {dry_run}")
    print("LOG_FILES:")
    for lf in log_files:
        print(f"  - {lf}")
    print("============================================================\n")

    print("[INFO] Building Pandora_T0 index from logs...")
    pandora_index = build_pandora_index(log_files, search_window)
    print(f"[INFO] Indexed candidates: {len(pandora_index)}\n")

    pattern = str(src_dir / "wvfFind_event*_trackID*_*.root")
    files = sorted(glob.glob(pattern))
    print(f"[INFO] Found ROOT files: {len(files)}\n")

    if not dry_run:
        dst_dir.mkdir(parents=True, exist_ok=True)

    n_copied = 0
    n_inrange = 0
    n_missing = 0
    n_unparsed = 0

    for fpath in files:
        key = extract_event_trackid_from_filename(fpath)
        if key is None:
            n_unparsed += 1
            print(f"[WARN] Cannot parse filename: {os.path.basename(fpath)}")
            continue

        event, trackid = key

        if key not in pandora_index:
            n_missing += 1
            print(f"[WARN] Not found in logs: event={event}, trackID={trackid} -> SKIP")
            continue

        t0 = pandora_index[key]

        if (t0 < a) or (t0 > b):
            dst_path = dst_dir / os.path.basename(fpath)
            if dry_run:
                print(f"[DRY] COPY (out of range) event={event}, trackID={trackid}, T0={t0} -> {dst_path}")
            else:
                shutil.copy2(fpath, dst_path)
                print(f"[COPY] event={event}, trackID={trackid}, T0={t0} -> {dst_path}")
            n_copied += 1
        else:
            print(f"[SKIP] (in range) event={event}, trackID={trackid}, T0={t0}")
            n_inrange += 1

    print("\n===== Summary =====")
    print(f"Total files scanned:        {len(files)}")
    print(f"Copied (out of [A,B]):      {n_copied}")
    print(f"Skipped (within [A,B]):     {n_inrange}")
    print(f"Skipped (missing in logs):  {n_missing}")
    print(f"Unparsed filenames:         {n_unparsed}")


if __name__ == "__main__":
    main()