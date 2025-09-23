import os
import re

# Input and output file paths
input_file = "./info_jeremy_stage1.txt"
output_file = "info_jeremy_stage2.txt"

# Storage for extracted data
extracted_lines = []
current_run = None
current_event = None

# Read the input file
with open(input_file, 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    line = line.strip()

    # Keep all existing content by default
    extracted_lines.append(line)

    # Extract run/subRun/event (from lines like: "[3rd record] run: 1000 subRun: 7 event: 2079")
    match_event = re.search(r'run:\s*(\d+)\s+subRun:\s*(\d+)\s+event:\s*(\d+)', line)
    if match_event:
        current_run = match_event.group(1)
        current_event = match_event.group(3)
        continue

    # Modify lines starting with "trk#"
    match_trk = re.search(r'\btrk#(\d+)\b', line)
    if match_trk:
        track_id = match_trk.group(1)

        # Defaults (use -1 for missing numeric values, 0 for PDG)
        pdg = 0
        true_energy = -1.0
        lifetime = -1.0

        # Robust regexes to handle both new and old formats and scientific notation
        m_pdg = re.search(r'PDG\s*:\s*(-?\d+)', line)
        m_ke = re.search(r'(?:Michel\s+)?True\s*K-energy\s*:\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*MeV', line)
        m_life = re.search(r'(?:MCTruth\s+muon\s+)?lifetime\s*\[us\]\s*:\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)', line)

        if m_pdg:
            pdg = int(m_pdg.group(1))
        if m_ke:
            true_energy = float(m_ke.group(1))
        if m_life:
            lifetime = float(m_life.group(1))

        # Build formatted summary line
        formatted_line = (
            f"Run: {current_run},  Event: {current_event},  TrackID: {track_id},  "
            f"PDG: {pdg},  TrueE[MeV]: {true_energy},  lifetime[us]: {lifetime}"
        )

        # Replace the last appended line (the raw trk# line) with the formatted summary
        extracted_lines[-1] = formatted_line

# Write extracted data to output file
with open(output_file, 'w') as f:
    for line in extracted_lines:
        f.write(line + "\n")

print(f"Processing complete. Data saved to {output_file}")
