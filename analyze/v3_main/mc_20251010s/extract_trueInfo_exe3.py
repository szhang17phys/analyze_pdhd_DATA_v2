import re
import argparse
import os

# ============================================================
# Parse command-line arguments
# ============================================================
parser = argparse.ArgumentParser(description="Extract true PDG, energy, Michel score, and Michel hits info")
parser.add_argument("--mcTruth_file", required=True, help="Input mcTruth txt file")
parser.add_argument("--wvfCoin_file", required=True, help="Input waveform coincidence count txt file")
parser.add_argument("--E_out", required=True, help="Output file for true energy (MeV)")
parser.add_argument("--PDG_out", required=True, help="Output file for true PDG codes")
parser.add_argument("--MS_out", required=True, help="Output file for Michel score")
parser.add_argument("--MH_out", required=True, help="Output file for Michel hits")
args = parser.parse_args()

mcTruth_file = args.mcTruth_file
wvfCoin_file = args.wvfCoin_file
E_path = args.E_out
PDG_path = args.PDG_out
MS_path = args.MS_out
MH_path = args.MH_out

print(f"[INFO] Using mcTruth file: {mcTruth_file}")
print(f"[INFO] Using wvfCoin file: {wvfCoin_file}")
print(f"[INFO] Output (E):   {E_path}")
print(f"[INFO] Output (PDG): {PDG_path}")
print(f"[INFO] Output (MS):  {MS_path}")
print(f"[INFO] Output (MH):  {MH_path}")

# ============================================================
# Ensure output directories exist
# ============================================================
for out_path in [E_path, PDG_path, MS_path, MH_path]:
    out_dir = os.path.dirname(out_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

# ============================================================
# Load mcTruth lines
# ============================================================
with open(mcTruth_file, "r") as f:
    filtered_lines = f.readlines()

# ============================================================
# Core extraction logic
# ============================================================
with open(E_path, "w") as E_out, \
     open(PDG_path, "w") as PDG_out, \
     open(MS_path, "w") as MS_out, \
     open(MH_path, "w") as MH_out:

    with open(wvfCoin_file, "r") as f:
        for line in f:
            match = re.search(r"event(\d+)_trackID(\d+)", line)
            if not match:
                continue

            event_target = int(match.group(1))
            track_target = int(match.group(2))

            found_match = False

            for idx, current_line in enumerate(filtered_lines):
                if "Run:" not in current_line:
                    continue

                evt_trk = re.search(r"Event:\s*(\d+),\s*TrackID:\s*(\d+)", current_line)
                if not evt_trk:
                    continue

                event = int(evt_trk.group(1))
                track = int(evt_trk.group(2))

                if event == event_target and track == track_target:
                    found_match = True

                    # -----------------------------
                    # Extract PDG
                    # -----------------------------
                    pdg_match = re.search(r"PDG:\s*([+-]?\d+)", current_line)
                    if pdg_match:
                        PDG_out.write(pdg_match.group(1) + "\n")
                    else:
                        PDG_out.write("NaN\n")

                    # -----------------------------
                    # Extract TrueE
                    # -----------------------------
                    trueE_match = re.search(
                        r"TrueE\[MeV\]:\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)",
                        current_line,
                    )
                    if trueE_match:
                        E_out.write(trueE_match.group(1) + "\n")
                    else:
                        E_out.write("NaN\n")

                    # -----------------------------
                    # Extract Michel score / hits
                    # They are expected on the line above Run/Event/TrackID
                    # -----------------------------
                    if idx > 0:
                        previous_line = filtered_lines[idx - 1]

                        ms_mh_match = re.search(
                            r"Michel score:\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?),\s*Michel hits:\s*(\d+)",
                            previous_line,
                        )

                        if ms_mh_match:
                            MS_out.write(ms_mh_match.group(1) + "\n")
                            MH_out.write(ms_mh_match.group(2) + "\n")
                        else:
                            MS_out.write("NaN\n")
                            MH_out.write("NaN\n")
                    else:
                        MS_out.write("NaN\n")
                        MH_out.write("NaN\n")

                    break

            if not found_match:
                PDG_out.write("NaN\n")
                E_out.write("NaN\n")
                MS_out.write("NaN\n")
                MH_out.write("NaN\n")

print("[SUCCESS] True PDG, TrueE, Michel score, and Michel hits extraction completed.")