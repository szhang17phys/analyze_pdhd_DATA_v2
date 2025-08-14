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
    
    # Keep all existing content
    extracted_lines.append(line)
    
    # Extract run and event number
    match_event = re.search(r'run: (\d+) subRun: (\d+) event: (\d+)', line)
    if match_event:
        current_run = match_event.group(1)
        current_event = match_event.group(3)
        continue
    

    # Modify lines starting with "trk#"
    match_trk = re.search(r'trk#(\d+)', line)
    if match_trk:
        track_id = match_trk.group(1)

        # Default values
        true_energy = -1
        lifetime = -1

        # Try to extract Michel energy and lifetime from the same line
        match_energy = re.search(r'Michel True K-energy\s*:\s*([0-9.]+)', line)
        match_lifetime = re.search(r'MCTruth muon lifetime\s*\[us\]\s*:\s*([0-9.]+)', line)
        if match_energy:
            true_energy = float(match_energy.group(1))
        if match_lifetime:
            lifetime = float(match_lifetime.group(1))

        formatted_line = (
            f"Run: {current_run},  Event: {current_event},  TrackID: {track_id},  "
            f"TrueE[MeV]: {true_energy},  lifetime[us]: {lifetime}"
        )
        extracted_lines[-1] = formatted_line  # Replace last appended line



# Write extracted data to output file
with open(output_file, 'w') as f:
    for line in extracted_lines:
        f.write(line + "\n")

print(f"Processing complete. Data saved to {output_file}")
