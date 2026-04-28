import re
import argparse
import os


# ============================================================
# Parse command-line arguments
# ============================================================
parser = argparse.ArgumentParser(description="Extract true PDG, energy, Michel score, and Michel hits info")
parser.add_argument("--mcTruth_file1", required=True, help="First input mcTruth txt file")
parser.add_argument("--mcTruth_file2", required=True, help="Second input mcTruth txt file")
parser.add_argument("--mcTruth_file3", required=True, help="Third input mcTruth txt file")
parser.add_argument("--wvfCoin_file", required=True, help="Input waveform coincidence count txt file")
parser.add_argument("--E_out", required=True, help="Output file for true energy (MeV)")
parser.add_argument("--PDG_out", required=True, help="Output file for true PDG codes")
parser.add_argument("--MS_out", required=True, help="Output file for Michel score")
parser.add_argument("--MH_out", required=True, help="Output file for Michel hits")
args = parser.parse_args()

mcTruth_file1 = args.mcTruth_file1
mcTruth_file2 = args.mcTruth_file2
mcTruth_file3 = args.mcTruth_file3
wvfCoin_file = args.wvfCoin_file
E_path = args.E_out
PDG_path = args.PDG_out
MS_path = args.MS_out
MH_path = args.MH_out

print(f"[INFO] Using mcTruth file1: {mcTruth_file1}")
print(f"[INFO] Using mcTruth file2: {mcTruth_file2}")
print(f"[INFO] Using mcTruth file3: {mcTruth_file3}")
print(f"[INFO] Using wvfCoin file: {wvfCoin_file}")
print(f"[INFO] Output (E):   {E_path}")
print(f"[INFO] Output (PDG): {PDG_path}")
print(f"[INFO] Output (MS):  {MS_path}")
print(f"[INFO] Output (MH):  {MH_path}")


# ============================================================
# Ensure output directory exists
# ============================================================
for out_path in [E_path, PDG_path, MS_path, MH_path]:
    out_dir = os.path.dirname(out_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)


# ============================================================
# Helper functions
# ============================================================
def normalize_file_id(file_id):
    if file_id is None:
        return None
    return file_id.strip().removeprefix("file")


# ============================================================
# Build lookup table from mcTruth files
# Key = (fileID, event, trackID)
# Val = (pdg, trueE, michelScore, michelHits)
# ============================================================
truth_lookup = {}

for mc_file in [mcTruth_file1, mcTruth_file2, mcTruth_file3]:
    print(f"[INFO] Loading mcTruth entries from: {mc_file}")

    current_file_id = None
    current_michel_score = ""
    current_michel_hits = ""

    with open(mc_file, "r") as f:
        for line in f:
            line = line.strip()

            # Example:
            # Michel score: 0.0567113,  Michel hits: 1
            m_ms_mh = re.search(
                r"Michel score:\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?),\s*Michel hits:\s*(\d+)",
                line
            )
            if m_ms_mh:
                current_michel_score = m_ms_mh.group(1)
                current_michel_hits = m_ms_mh.group(2)
                continue

            # Example:
            # filename: 257707_35_1_20251204T225143Z
            m_file = re.search(r"filename:\s*([^\s]+)", line)
            if m_file:
                current_file_id = normalize_file_id(m_file.group(1))
                continue

            # Example:
            # Run: 20250627,  Event: 443,  TrackID: 15,  PDG: -11,  TrueE[MeV]: 28.7254, ...
            m_evt = re.search(
                r"Event:\s*(\d+),\s*TrackID:\s*(\d+)", line
            )
            if not m_evt:
                continue

            if current_file_id is None:
                print(f"[WARNING] Found Event/TrackID before filename in {mc_file}:")
                print(f"          {line}")
                continue

            event = int(m_evt.group(1))
            track = int(m_evt.group(2))

            pdg_match = re.search(r"PDG:\s*([+-]?\d+)", line)
            trueE_match = re.search(
                r"TrueE\[MeV\]:\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)",
                line,
            )

            pdg_val = pdg_match.group(1) if pdg_match else ""
            trueE_val = trueE_match.group(1) if trueE_match else ""

            key = (current_file_id, event, track)

            if key in truth_lookup:
                print(
                    f"[WARNING] Duplicate mcTruth key found for "
                    f"fileID={current_file_id}, event={event}, track={track}. "
                    f"Keeping the first occurrence."
                )
            else:
                truth_lookup[key] = (
                    pdg_val,
                    trueE_val,
                    current_michel_score,
                    current_michel_hits,
                )

print(f"[INFO] Total unique mcTruth entries loaded: {len(truth_lookup)}")


# ============================================================
# Extract true info using waveform coincidence list
# ============================================================
n_found = 0
n_total = 0

with open(E_path, "w") as E_out, \
     open(PDG_path, "w") as PDG_out, \
     open(MS_path, "w") as MS_out, \
     open(MH_path, "w") as MH_out:

    with open(wvfCoin_file, "r") as f:
        for line in f:
            # Example:
            # wvfFind_file259389_92_1_20251209T092029Z_event650_trackID5_opNum2.root: 2
            m = re.search(
                r"wvfFind_(file\d+_\d+_\d+_\d+T\d+Z)_event(\d+)_trackID(\d+)",
                line
            )
            if not m:
                continue

            n_total += 1

            file_id_wave = normalize_file_id(m.group(1))
            event_target = int(m.group(2))
            track_target = int(m.group(3))

            key = (file_id_wave, event_target, track_target)

            if key in truth_lookup:
                pdg_val, trueE_val, ms_val, mh_val = truth_lookup[key]

                PDG_out.write(pdg_val + "\n")
                E_out.write(trueE_val + "\n")
                MS_out.write(ms_val + "\n")
                MH_out.write(mh_val + "\n")

                n_found += 1
            else:
                print(
                    f"[WARNING] No match found for "
                    f"fileID={file_id_wave}, event={event_target}, track={track_target}"
                )

                PDG_out.write("\n")
                E_out.write("\n")
                MS_out.write("\n")
                MH_out.write("\n")

print(f"[SUCCESS] True PDG, TrueE, Michel score, and Michel hits extraction completed.")
print(f"[INFO] Matched entries: {n_found}/{n_total}")