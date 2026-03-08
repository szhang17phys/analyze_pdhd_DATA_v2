#!/usr/bin/env python3
import os
import re
import glob
import shutil
import argparse
from pathlib import Path

# ============================================================
# ====================== ARGUMENT PARSER =====================
# ============================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description="Copy waveform ROOT files whose Pandora_T0 is outside a given window [A, B]."
    )

    parser.add_argument(
        "--src_dir",
        required=True,
        help="Source directory containing waveform ROOT files."
    )

    parser.add_argument(
        "--dst_dir",
        required=True,
        help="Destination directory for copied ROOT files."
    )

    parser.add_argument(
        "--a",
        type=float,
        required=True,
        help="Lower bound of Pandora_T0 cut window [A, B] in ms."
    )

    parser.add_argument(
        "--b",
        type=float,
        required=True,
        help="Upper bound of Pandora_T0 cut window [A, B] in ms."
    )

    parser.add_argument(
        "--log_files",
        nargs="+",
        required=True,
        help="One or more log files used to build Pandora_T0 index."
    )

    parser.add_argument(
        "--search_window",
        type=int,
        default=4,
        help="Number of lines to search after Run/Event/TrackID line for Pandora_T0. Default: 4"
    )

    parser.add_argument(
        "--dry_run",
        action="store_true",
        help="If set, do not copy files; only print actions."
    )

    return parser.parse_args()


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
    args = parse_args()

    src_dir = Path(args.src_dir)
    dst_dir = Path(args.dst_dir)
    log_files = [Path(x) for x in args.log_files]
    a = args.a
    b = args.b
    search_window = args.search_window
    dry_run = args.dry_run

    print("============================================================")
    print("CONFIG SUMMARY")
    print("============================================================")
    print(f"SRC_DIR         : {src_dir}")
    print(f"DST_DIR         : {dst_dir}")
    print(f"Cut window [A,B]: [{a}, {b}]")
    print(f"SEARCH_WINDOW   : {search_window}")
    print(f"DRY_RUN         : {dry_run}")
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