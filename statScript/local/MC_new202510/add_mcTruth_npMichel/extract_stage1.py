import os
import re
import argparse

# ================================================================
# Require data_dir to be passed from shell script
# ================================================================
parser = argparse.ArgumentParser(description="Stage 1 extraction script")
parser.add_argument("--data_dir", required=True, help="Path to input data directory")
args = parser.parse_args()

data_dir = args.data_dir
output_file = "info_jeremy_stage1.txt"

print(f"[extract_stage1] Using data_dir: {data_dir}")
print(f"[extract_stage1] Output file: {output_file}")
# ================================================================




# Storage for extracted data
extracted_lines = []
latest_trk = None
pending_trks = []
pending_pdg = None  # e.g., "PDG : 11"
have_ke_for_trk = False  # track-level flags
have_life_for_trk = False

# Function to convert number to ordinal (1st, 2nd, 3rd, etc.)
def ordinal(n):
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"

# Helper: ensure we append to the current track line
def append_to_current_trk(text):
    if extracted_lines and extracted_lines[-1].startswith("trk#"):
        extracted_lines[-1] += text

# Process each text file in the directory
for file_name in sorted(os.listdir(data_dir)):
    file_path = os.path.join(data_dir, file_name)

    # Only process .txt files
    if not file_name.endswith(".txt"):
        continue

    extracted_lines.append(f"\n\n\n===== Processing file: {file_name} =====\n")

    with open(file_path, 'r') as f:
        lines = f.readlines()

    pending_trks = []
    pending_pdg = None
    latest_trk = None
    have_ke_for_trk = False
    have_life_for_trk = False

    for i, line in enumerate(lines):
        line = line.strip()

        # Extract root file path
        match_root = re.search(r'Opened input file "(.*?)"', line)
        if match_root:
            extracted_lines.append(match_root.group(1))
            continue

        # Extract event record
        match_event = re.search(r'processing the (\d+)(?:st|nd|rd|th) record.*?run: (\d+) subRun: (\d+) event: (\d+)', line)
        if match_event:
            record_number = int(match_event.group(1))
            extracted_lines.append("")  # blank line before each event
            extracted_lines.append(f"[{ordinal(record_number)} record] run: {match_event.group(2)} subRun: {match_event.group(3)} event: {match_event.group(4)}")
            continue

        # Extract track number
        match_trk = re.search(r'(trk#\d+)', line)
        if match_trk:
            latest_trk = match_trk.group(1)
            pending_trks.append(latest_trk)
            extracted_lines.append(latest_trk)
            # reset per-track flags
            pending_pdg = None
            have_ke_for_trk = False
            have_life_for_trk = False
            continue

        # Detect PDG: explicit "(PDG: 11)" or fallback via observed charge "(e+)" / "(e-)"
        match_pdg = re.search(r'\(PDG:\s*(-?\d+)\)', line)
        if match_pdg:
            pending_pdg = f"PDG : {match_pdg.group(1)}"
        else:
            if "(e+)" in line:
                pending_pdg = "PDG : -11"
            elif "(e-)" in line:
                pending_pdg = "PDG : 11"

        # If we have a track line started, append PDG as soon as we know it (once)
        if pending_pdg and latest_trk and extracted_lines and extracted_lines[-1].startswith("trk#") and "PDG :" not in extracted_lines[-1]:
            append_to_current_trk(f"  {pending_pdg}")

        # Extract Michel True K-energy (and possibly lifetime on same line)
        # Examples:
        # "Michel True K-energy : 36.3254 MeV  /  lifetime [us]: 0.480236"
        ke_life_match = re.search(
            r'Michel True K-energy\s*:\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*MeV(?:\s*/\s*lifetime\s*\[us\]\s*:\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?))?',
            line
        )
        if ke_life_match and latest_trk and extracted_lines and extracted_lines[-1].startswith("trk#"):
            ke_val = ke_life_match.group(1)
            life_val = ke_life_match.group(2)  # may be None
            # Ensure PDG appears first
            if "PDG :" not in extracted_lines[-1] and pending_pdg:
                append_to_current_trk(f"  {pending_pdg}")
            # Append K-energy
            append_to_current_trk(f"  /  True K-energy : {ke_val} MeV")
            have_ke_for_trk = True
            # If lifetime is on the same line, append it too
            if life_val is not None:
                append_to_current_trk(f"  /  lifetime [us]: {life_val}")
                have_life_for_trk = True
            continue

        # Extract lifetime if it appears later on its own line
        # Accept both "lifetime [us]:" and "MCTruth muon lifetime [us]:"
        life_alone = re.search(
            r'(?:MCTruth\s+muon\s+)?lifetime\s*\[us\]\s*:\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)',
            line
        )
        if life_alone and latest_trk and extracted_lines and extracted_lines[-1].startswith("trk#") and not have_life_for_trk:
            life_val = life_alone.group(1)
            # Ensure PDG/K-energy ordering is sensible
            if "PDG :" not in extracted_lines[-1] and pending_pdg:
                append_to_current_trk(f"  {pending_pdg}")
            if "True K-energy" not in extracted_lines[-1]:
                # Lifetime arrived before K-energy; still append gracefully
                append_to_current_trk(f"  /  lifetime [us]: {life_val}")
            else:
                append_to_current_trk(f"  /  lifetime [us]: {life_val}")
            have_life_for_trk = True
            continue

    extracted_lines.append("\n")  # Add a blank line after processing each file

# Write extracted data to output file
with open(output_file, 'w') as f:
    for line in extracted_lines:
        f.write(line + "\n")

print(f"Aggregation complete. Data saved to {output_file}")
