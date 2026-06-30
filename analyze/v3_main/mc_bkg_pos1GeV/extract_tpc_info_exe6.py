import re
import argparse


parser = argparse.ArgumentParser(
    description="Extract TPC position / Michel score / Michel hits / truth info matched to muon peak candidates."
)

parser.add_argument("--mcTruth_file1", required=True, help="Input mcTruth txt file 1.")
parser.add_argument("--mcTruth_file2", required=True, help="Input mcTruth txt file 2.")
parser.add_argument("--mcTruth_file3", required=True, help="Input mcTruth txt file 3.")
parser.add_argument("--muon_txt", required=True, help="Muon peak txt file.")

parser.add_argument("--x_out", required=True, help="Output txt for X position.")
parser.add_argument("--y_out", required=True, help="Output txt for Y position.")
parser.add_argument("--z_out", required=True, help="Output txt for Z position.")
parser.add_argument("--score_out", required=True, help="Output txt for Michel score.")
parser.add_argument("--hits_out", required=True, help="Output txt for Michel hits.")
parser.add_argument("--E_out", required=True, help="Output txt for true energy.")
parser.add_argument("--PDG_out", required=True, help="Output txt for PDG.")
parser.add_argument("--lifetime_out", required=True, help="Output txt for lifetime.")

args = parser.parse_args()


def normalize_file_id(file_id):
    """
    Normalize file ID so that:
      waveform side:  file265865_123_1_20251210T154811Z
      mcTruth side:   265865_123_1_20251210T154811Z
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
E_path = args.E_out
P_path = args.PDG_out
L_path = args.lifetime_out


# Open output files
with open(x_path, "w") as x_out, \
     open(y_path, "w") as y_out, \
     open(z_path, "w") as z_out, \
     open(S_path, "w") as S_out, \
     open(H_path, "w") as H_out, \
     open(E_path, "w") as E_out, \
     open(P_path, "w") as P_out, \
     open(L_path, "w") as L_out:

    # ================================================================
    # Build lookup table from mcTruth txt files
    # Key = (fileID, event, trackID)
    # Val = (x, y, z, score, hits, pdg, trueE, lifetime)
    # ================================================================
    truth_lookup = {}

    mcTruth_files = [
        args.mcTruth_file1,
        args.mcTruth_file2,
        args.mcTruth_file3
    ]

    for txt_file in mcTruth_files:
        print(f"[INFO] Reading mcTruth txt: {txt_file}")

        with open(txt_file, "r") as f:
            lines = f.readlines()

        current_fileid = None

        for i, line in enumerate(lines):
            line_stripped = line.strip()

            # filename: 257708_39_1_20251204T232000Z
            m_file = re.search(r"filename:\s*([^\s]+)", line_stripped)
            if m_file:
                current_fileid = normalize_file_id(m_file.group(1))
                continue

            # Run/Event/TrackID/PDG/TrueE/lifetime line
            evt_trk = re.search(
                r"Event:\s*(\d+),\s*TrackID:\s*(\d+),\s*PDG:\s*([-\d]+),\s*TrueE\[MeV\]:\s*([-\dEe+\.]+),\s*lifetime\[us\]:\s*([-\dEe+\.]+)",
                line_stripped
            )
            if not evt_trk:
                continue

            if current_fileid is None:
                print(f"[WARNING] Found Event/TrackID before filename in {txt_file}:")
                print(f"          {line_stripped}")
                continue

            event = int(evt_trk.group(1))
            track = int(evt_trk.group(2))
            pdg_val = evt_trk.group(3)
            trueE_val = evt_trk.group(4)
            lifetime_val = evt_trk.group(5)

            # Michel score / hits: two lines above
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

            # End(x, y, z): two lines below
            x_val, y_val, z_val = "NaN", "NaN", "NaN"
            if i + 2 < len(lines):
                end_line = lines[i + 2].strip()
                end_match = re.search(
                    r"End\(x, y, z\)\s*=\s*\(([-\dEe+\.]+),\s*([-\dEe+\.]+),\s*([-\dEe+\.]+)\)",
                    end_line
                )
                if end_match:
                    x_val = end_match.group(1)
                    y_val = end_match.group(2)
                    z_val = end_match.group(3)

            key = (current_fileid, event, track)

            if key in truth_lookup:
                print(
                    f"[WARNING] Duplicate mcTruth entry for "
                    f"fileID={current_fileid}, event={event}, trackID={track}. "
                    f"Overwriting previous values."
                )

            truth_lookup[key] = (
                x_val, y_val, z_val,
                score_val, hits_val,
                pdg_val, trueE_val, lifetime_val
            )

    print(f"[INFO] Total mcTruth candidates indexed: {len(truth_lookup)}")

    # ================================================================
    # Process each line in muon txt
    # ================================================================
    n_total = 0
    n_found = 0

    with open(args.muon_txt, "r") as f:
        for line in f:
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

            if key in truth_lookup:
                x_val, y_val, z_val, score_val, hits_val, pdg_val, trueE_val, lifetime_val = truth_lookup[key]

                x_out.write(x_val + "\n")
                y_out.write(y_val + "\n")
                z_out.write(z_val + "\n")
                S_out.write(score_val + "\n")
                H_out.write(hits_val + "\n")
                E_out.write(trueE_val + "\n")
                P_out.write(pdg_val + "\n")
                L_out.write(lifetime_val + "\n")

                n_found += 1
            else:
                print(
                    f"[WARNING] No match found for "
                    f"fileID={file_target}, event={event_target}, trackID={track_target}"
                )

                x_out.write("NaN\n")
                y_out.write("NaN\n")
                z_out.write("NaN\n")
                S_out.write("NaN\n")
                H_out.write("NaN\n")
                E_out.write("NaN\n")
                P_out.write("NaN\n")
                L_out.write("NaN\n")

    print(f"[SUCCESS] TPC / truth info extraction completed.")
    print(f"[INFO] Matched entries: {n_found}/{n_total}")