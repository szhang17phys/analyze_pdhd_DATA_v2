import os
import re

# Input and output directories
data_dir = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/t0_rootFiles/new20250808_MC/mcTruth_20250811"
output_file = "info_jeremy_stage1.txt"

# Storage for extracted data
extracted_lines = []
latest_trk = None
pending_trks = []

# Function to convert number to ordinal (1st, 2nd, 3rd, etc.)
def ordinal(n):
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"

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
            extracted_lines.append("")  # Add a blank line before each event
            extracted_lines.append(f"[{ordinal(record_number)} record] run: {match_event.group(2)} subRun: {match_event.group(3)} event: {match_event.group(4)}")
            continue
        
        # Extract track number
        match_trk = re.search(r'(trk#\d+)', line)
        if match_trk:
            pending_trks.append(match_trk.group(1))
            extracted_lines.append(match_trk.group(1))  # Always keep trk#
            continue


        # Extract Michel True K-energy
        match_ke = re.search(r'Michel True K-energy\s*:\s*[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?\s*MeV', line)
        if match_ke and extracted_lines and extracted_lines[-1].startswith("trk#"):
            extracted_lines[-1] += f"   {match_ke.group(0)}"
            continue

        # Extract MCTruth muon lifetime
        match_life = re.search(r'MCTruth muon lifetime\s*\[us\]\s*:\s*[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', line)
        if match_life and extracted_lines and extracted_lines[-1].startswith("trk#"):
            extracted_lines[-1] += f" / {match_life.group(0)}"
            continue

    
    extracted_lines.append("\n")  # Add a blank line after processing each file

# Write extracted data to output file
with open(output_file, 'w') as f:
    for line in extracted_lines:
        f.write(line + "\n")

print(f"Aggregation complete. Data saved to {output_file}")
