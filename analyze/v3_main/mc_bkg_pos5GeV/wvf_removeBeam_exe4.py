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
        (fileID:str, event:int, trackID:int) -> Pandora_T0[ms]:float

    We detect a block like:
      FileID: 265273_188_1_20251209T170358Z
      Run: 20250627,  Event: 870,  TrackID: 5
      ...
      Pandora_T0[ms]: -1.61292

    Then we store:
      ("265273_188_1_20251209T170358Z", 870, 5) -> -1.61292
    """
    fileid_re = re.compile(r"FileID:\s*([^\s]+)")
    key_re = re.compile(r"Run:\s*\d+,\s*Event:\s*(\d+),\s*TrackID:\s*(\d+)")
    pandora_re = re.compile(r"Pandora_T0\[ms\]:\s*([+-]?\d+(?:\.\d+)?)")

    index = {}

    for log_path in log_paths:
        if not log_path.exists():
            print(f"[ERROR] Log file not found: {log_path}")
            continue

        print(f"[INFO] Reading {log_path}")
        with log_path.open("r", errors="replace") as f:
            current_fileid = None
            pending_key = None
            remaining = 0

            for line in f:
                mf = fileid_re.search(line)
                if mf:
                    current_fileid = mf.group(1)
                    if pending_key is not None:
                        print(
                            f"[WARN] New FileID encountered before Pandora_T0 was found "
                            f"for pending key {pending_key} in {log_path}"
                        )
                        pending_key = None
                        remaining = 0

                if pending_key is None:
                    m = key_re.search(line)
                    if m:
                        event = int(m.group(1))
                        trackid = int(m.group(2))

                        if current_fileid is None:
                            print(f"[WARN] Missing FileID before Event/TrackID in {log_path}")
                            continue

                        pending_key = (current_fileid, event, trackid)
                        remaining = search_window
                    continue

                mp = pandora_re.search(line)
                if mp:
                    if pending_key in index:
                        print(
                            f"[WARN] Duplicate Pandora_T0 entry for key {pending_key} "
                            f"in {log_path}; overwriting old value {index[pending_key]} "
                            f"with new value {float(mp.group(1))}"
                        )
                    index[pending_key] = float(mp.group(1))
                    pending_key = None
                    remaining = 0
                    continue

                remaining -= 1
                if remaining <= 0:
                    print(f"[WARN] Pandora_T0 not found within search window for key {pending_key} in {log_path}")
                    pending_key = None

    return index



def extract_fileid_event_trackid_from_filename(fname):
    """
    Parse fileID, event, and trackID from filenames like:
      wvfFind_file259389_92_1_20251209T092029Z_event650_trackID5_opNum2.root
      wvfFind_file263559_139_1_20251205T011331Z_event1215_trackID7_opNum9_merged.root
      wvfFind_file259418_14_1_20251209T121234Z_event777_trackID24_opNum6_2.root
    """
    base = os.path.basename(fname)
    m = re.search(
        r"wvfFind_file(\d+_\d+_\d+_\d+T\d+Z)_event(\d+)_trackID(\d+)_",
        base
    )
    if not m:
        return None

    fileid = m.group(1)
    event = int(m.group(2))
    trackid = int(m.group(3))
    return fileid, event, trackid


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

    pattern = str(src_dir / "wvfFind_file*_event*_trackID*_*.root")
    files = sorted(glob.glob(pattern))
    print(f"[INFO] Found ROOT files: {len(files)}\n")

    if not dry_run:
        dst_dir.mkdir(parents=True, exist_ok=True)

    n_copied = 0
    n_inrange = 0
    n_missing = 0
    n_unparsed = 0

    for fpath in files:
        key = extract_fileid_event_trackid_from_filename(fpath)
        if key is None:
            n_unparsed += 1
            print(f"[WARN] Cannot parse filename: {os.path.basename(fpath)}")
            continue

        fileid, event, trackid = key

        if key not in pandora_index:
            n_missing += 1
            print(
                f"[WARN] Not found in logs: "
                f"fileID={fileid}, event={event}, trackID={trackid} -> SKIP"
            )
            continue

        t0 = pandora_index[key]

        if (t0 < a) or (t0 > b):
            dst_path = dst_dir / os.path.basename(fpath)
            if dry_run:
                print(
                    f"[DRY] COPY (out of range) "
                    f"fileID={fileid}, event={event}, trackID={trackid}, T0={t0} -> {dst_path}"
                )
            else:
                shutil.copy2(fpath, dst_path)
                print(
                    f"[COPY] fileID={fileid}, event={event}, trackID={trackid}, T0={t0} -> {dst_path}"
                )
            n_copied += 1
        else:
            print(
                f"[SKIP] (in range) "
                f"fileID={fileid}, event={event}, trackID={trackid}, T0={t0}"
            )
            n_inrange += 1

    print("\n===== Summary =====")
    print(f"Total files scanned:        {len(files)}")
    print(f"Copied (out of [A,B]):      {n_copied}")
    print(f"Skipped (within [A,B]):     {n_inrange}")
    print(f"Skipped (missing in logs):  {n_missing}")
    print(f"Unparsed filenames:         {n_unparsed}")


if __name__ == "__main__":
    main()