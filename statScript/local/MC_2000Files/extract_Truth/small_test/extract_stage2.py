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
        michel_match = re.search(r'looking at michel', line)
        michel_status = "  Yes" if michel_match else "  No"
        formatted_line = f"Run: {current_run},  Event: {current_event},  TrackID: {track_id}{michel_status}"
        extracted_lines[-1] = formatted_line  # Replace last appended line

# Write extracted data to output file
with open(output_file, 'w') as f:
    for line in extracted_lines:
        f.write(line + "\n")

print(f"Processing complete. Data saved to {output_file}")
