import os
import re

# Input and output file paths
initial_file = "../original_list/initial_print.txt"
info_file = "./info_jeremy_stage2.txt"
output_file = "../original_list/updated_initial_print.txt"

# Read the second file into a dictionary for fast lookup
info_dict = {}
with open(info_file, 'r') as f:
    for line in f:
        match = re.search(r'Run: (\d+),\s+Event: (\d+),\s+TrackID: (\d+)\s+(Yes|No)', line)
        if match:
            run, event, track_id, status = match.groups()
            info_dict[(run, event, track_id)] = "1" if status == "Yes" else "0"

# Process the first file and update required lines
updated_lines = []
with open(initial_file, 'r') as f:
    for line in f:
        line = line.strip()
        match = re.search(r'Run: (\d+),\s+Event: (\d+),\s+TrackID: (\d+)', line)
        if match:
            run, event, track_id = match.groups()
            true_michel = info_dict.get((run, event, track_id), "N/A")
            updated_line = f"Run: {run},  Event: {event},  TrackID: {track_id},    True Michel: {true_michel}"
            updated_lines.append(updated_line)
        else:
            updated_lines.append(line)

# Write updated content to a new file
with open(output_file, 'w') as f:
    for line in updated_lines:
        f.write(line + "\n")

print(f"Processing complete. Data saved to {output_file}")
