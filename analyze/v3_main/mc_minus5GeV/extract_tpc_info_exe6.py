import re
import argparse


parser = argparse.ArgumentParser(
    description="Extract TPC position / Michel score / Michel hits info matched to muon peak candidates."
)

parser.add_argument(
    "--filtered_txts",
    nargs="+",
    required=True,
    help="One or more filtered input txt files."
)
parser.add_argument("--muon_txt", required=True, help="Muon peak txt file.")

parser.add_argument("--x_out", required=True, help="Output txt for X position.")
parser.add_argument("--y_out", required=True, help="Output txt for Y position.")
parser.add_argument("--z_out", required=True, help="Output txt for Z position.")
parser.add_argument("--score_out", required=True, help="Output txt for Michel score.")
parser.add_argument("--hits_out", required=True, help="Output txt for Michel hits.")

args = parser.parse_args()


def normalize_file_id(file_id):
    """
    Normalize file ID so that:
      waveform side:  file265865_123_1_20251210T154811Z
      filtered txt:   265865_123_1_20251210T154811Z
    become the same key.
    """
    if file_id is None:
        return None
    return file_id.strip().removeprefix("file")


# Define output file paths
x_path = args.x_out
y_path = args.y_out
z_path = args.z_out
S_path = args.score_out
H_path = args.hits_out


# Open output files in write mode
with open(x_path, "w") as x_out, open(y_path, "w") as y_out, open(z_path, "w") as z_out, \
     open(S_path, "w") as S_out, open(H_path, "w") as H_out:

    #================================================================
    # Build lookup table from filtered txt files
    # Key = (fileID, event, trackID)
    # Val = (x, y, z, score, hits)
    #================================================================
    filtered_lookup = {}

    for txt_file in args.filtered_txts:
        print(f"[INFO] Reading filtered txt: {txt_file}")

        with open(txt_file, "r") as f:
            lines = f.readlines()

        current_fileid = None

        for i, line in enumerate(lines):
            line_stripped = line.strip()

            # Example:
            # filename: 265865_123_1_20251210T154811Z
            m_file = re.search(r"filename:\s*([^\s]+)", line_stripped)
            if m_file:
                current_fileid = normalize_file_id(m_file.group(1))
                continue

            # Example:
            # Run: 20250627,  Event: 332,  TrackID: 3
            evt_trk = re.search(r"Event:\s*(\d+),\s*TrackID:\s*(\d+)", line_stripped)
            if not evt_trk:
                continue

            if current_fileid is None:
                print(f"[WARNING] Found Event/TrackID before filename in {txt_file}:")
                print(f"          {line_stripped}")
                continue

            event = int(evt_trk.group(1))
            track = int(evt_trk.group(2))

            #------------------------------------------------
            # Extract Michel score and hits
            # In the filtered txt structure, the layout is:
            #   Michel score: ...
            #   filename: ...
            #   Run: ..., Event: ..., TrackID: ...
            # so score/hits are two lines above the Run/Event/TrackID line
            #------------------------------------------------
            score_val = "NaN"
            hits_val = "NaN"
            if i >= 2:
                score_line = lines[i - 2].strip()
                ms_match = re.search(
                    r"Michel score:\s*([0-9Ee+\-\.]+),\s*Michel hits:\s*(\d+)",
                    score_line
                )
                if ms_match:
                    score_val = ms_match.group(1)
                    hits_val = ms_match.group(2)

            #------------------------------------------------
            # Extract End(x, y, z) (two lines below)
            #------------------------------------------------
            x_val, y_val, z_val = "NaN", "NaN", "NaN"
            if i + 2 < len(lines):
                end_line = lines[i + 2].strip()
                end_match = re.search(
                    r"End\(x, y, z\)\s*=\s*\(([-\d\.]+),\s*([-\d\.]+),\s*([-\d\.]+)\)",
                    end_line
                )
                if end_match:
                    x_val = end_match.group(1)
                    y_val = end_match.group(2)
                    z_val = end_match.group(3)

            key = (current_fileid, event, track)

            if key in filtered_lookup:
                print(
                    f"[WARNING] Duplicate filtered entry for "
                    f"fileID={current_fileid}, event={event}, trackID={track}. "
                    f"Overwriting previous values."
                )

            filtered_lookup[key] = (x_val, y_val, z_val, score_val, hits_val)

    print(f"[INFO] Total filtered candidates indexed: {len(filtered_lookup)}")

    #================================================================
    # Process each line in muon txt
    #================================================================
    n_total = 0
    n_found = 0

    with open(args.muon_txt, "r") as f:
        for line in f:
            # Example:
            # /path/to/wvfFind_file265865_123_1_20251210T154811Z_event332_trackID3_opNum9.root: ...
            match = re.search(
                r"wvfFind_(file\d+_\d+_\d+_\d+T\d+Z)_event(\d+)_trackID(\d+)",
                line
            )
            if not match:
                continue

            n_total += 1

            file_target = normalize_file_id(match.group(1))
            event_target = int(match.group(2))
            track_target = int(match.group(3))

            key = (file_target, event_target, track_target)

            if key in filtered_lookup:
                x_val, y_val, z_val, score_val, hits_val = filtered_lookup[key]

                S_out.write(score_val + "\n")
                H_out.write(hits_val + "\n")
                x_out.write(x_val + "\n")
                y_out.write(y_val + "\n")
                z_out.write(z_val + "\n")

                n_found += 1
            else:
                print(
                    f"[WARNING] No match found for "
                    f"fileID={file_target}, event={event_target}, trackID={track_target}"
                )
                S_out.write("NaN\n")
                H_out.write("NaN\n")
                x_out.write("NaN\n")
                y_out.write("NaN\n")
                z_out.write("NaN\n")

    print(f"[SUCCESS] TPC info extraction completed.")
    print(f"[INFO] Matched entries: {n_found}/{n_total}")