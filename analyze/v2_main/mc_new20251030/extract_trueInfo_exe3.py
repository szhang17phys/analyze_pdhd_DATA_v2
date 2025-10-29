import re
import argparse
import os

# ============================================================
# Parse command-line arguments
# ============================================================
parser = argparse.ArgumentParser(description="Extract true PDG and energy info")
parser.add_argument("--mcTruth_file", required=True, help="Input mcTruth txt file")
parser.add_argument("--wvfCoin_file", required=True, help="Input waveform coincidence count txt file")
parser.add_argument("--E_out", required=True, help="Output file for true energy (MeV)")
parser.add_argument("--PDG_out", required=True, help="Output file for true PDG codes")
args = parser.parse_args()

mcTruth_file = args.mcTruth_file
wvfCoin_file = args.wvfCoin_file
E_path = args.E_out
PDG_path = args.PDG_out

print(f"[INFO] Using mcTruth file: {mcTruth_file}")
print(f"[INFO] Using wvfCoin file: {wvfCoin_file}")
print(f"[INFO] Output (E):  {E_path}")
print(f"[INFO] Output (PDG): {PDG_path}")

# ============================================================
# Ensure output directory exists
# ============================================================
for out_path in [E_path, PDG_path]:
    out_dir = os.path.dirname(out_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

# ============================================================
# Core extraction logic
# ============================================================
with open(E_path, "w") as E_out, open(PDG_path, "w") as PDG_out:

    # Load mcTruth lines
    with open(mcTruth_file, "r") as f:
        filtered_lines = f.readlines()

    # Process each wvfCoin line
    with open(wvfCoin_file, "r") as f:
        for line in f:
            match = re.search(r"event(\d+)_trackID(\d+)", line)
            if not match:
                continue

            event_target = int(match.group(1))
            track_target = int(match.group(2))

            for current_line in filtered_lines:
                if "Run:" not in current_line:
                    continue

                evt_trk = re.search(r"Event:\s*(\d+),\s*TrackID:\s*(\d+)", current_line)
                if not evt_trk:
                    continue

                event = int(evt_trk.group(1))
                track = int(evt_trk.group(2))

                if event == event_target and track == track_target:
                    pdg_match = re.search(r"PDG:\s*([+-]?\d+)", current_line)
                    if pdg_match:
                        PDG_out.write(pdg_match.group(1) + "\n")

                    trueE_match = re.search(
                        r"TrueE\[MeV\]:\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)",
                        current_line,
                    )
                    if trueE_match:
                        E_out.write(trueE_match.group(1) + "\n")
                    break

print("[SUCCESS] True PDG and TrueE extraction completed.")
