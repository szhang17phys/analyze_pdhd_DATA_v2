import os
import glob

# ================================================================
# Define file names
# ================================================================
event_file = "./newResult/eventID_filtered.txt"
track_file = "./newResult/trackID_filtered.txt"
opchs_file = "./newResult/opchs_filtered.txt"

output_dir = "./sorted_candidates_list"
os.makedirs(output_dir, exist_ok=True)

# ================================================================
# Clean old sorted files before writing new ones
# ================================================================
old_files = glob.glob(os.path.join(output_dir, "*.txt"))
if old_files:
    print(f"[sort_script] Removing {len(old_files)} old files in {output_dir}/")
    for f in old_files:
        os.remove(f)
else:
    print(f"[sort_script] No old output files to remove.")

# ================================================================
# Read the data from all three input files
# ================================================================
with open(event_file, "r") as f_event, open(track_file, "r") as f_track, open(opchs_file, "r") as f_opchs:
    event_lines = f_event.readlines()
    track_lines = f_track.readlines()
    opchs_lines = f_opchs.readlines()

# Create aligned tuples and sort by event ID
event_data = [
    (int(event_lines[i].strip()), track_lines[i].strip(), opchs_lines[i].strip())
    for i in range(len(event_lines))
]
event_data.sort(key=lambda x: x[0])

# ================================================================
# Write sorted data back to output files
# ================================================================
with open(os.path.join(output_dir, "eventID_filtered_sorted.txt"), "w") as f_event_out, \
     open(os.path.join(output_dir, "trackID_filtered_sorted.txt"), "w") as f_track_out, \
     open(os.path.join(output_dir, "opchs_filtered_sorted.txt"), "w") as f_opchs_out:

    for event, track, opchs in event_data:
        f_event_out.write(f"{event}\n")
        f_track_out.write(f"{track}\n")
        f_opchs_out.write(f"{opchs}\n")

print("Sorting complete. Sorted files saved in:")
print(f"- {output_dir}/eventID_filtered_sorted.txt")
print(f"- {output_dir}/trackID_filtered_sorted.txt")
print(f"- {output_dir}/opchs_filtered_sorted.txt")
