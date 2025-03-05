# Define file names
event_file = "eventID_filtered.txt"
track_file = "trackID_filtered.txt"
opchs_file = "opchs_filtered.txt"

# Read the data from all three files
with open(event_file, "r") as f_event, open(track_file, "r") as f_track, open(opchs_file, "r") as f_opchs:
    event_lines = f_event.readlines()
    track_lines = f_track.readlines()
    opchs_lines = f_opchs.readlines()

# Convert event ID to integers for sorting, keeping all data aligned
# Create a list of tuples---
event_data = [(int(event_lines[i].strip()), track_lines[i].strip(), opchs_lines[i].strip()) for i in range(len(event_lines))]

# Sort based on event ID (first element of the tuple)
# Ascending order is the default for sort() in Python---
event_data.sort(key=lambda x: x[0])

# Write sorted data back to files
with open("eventID_filtered_sorted.txt", "w") as f_event_out, \
     open("trackID_filtered_sorted.txt", "w") as f_track_out, \
     open("opchs_filtered_sorted.txt", "w") as f_opchs_out:

    for event, track, opchs in event_data:
        f_event_out.write(f"{event}\n")       # Write event ID
        f_track_out.write(f"{track}\n")       # Write track ID
        f_opchs_out.write(f"{opchs}\n")       # Write full line of opchs values

print("Sorting complete. Sorted files saved as:")
print("- eventID_filtered_sorted.txt")
print("- trackID_filtered_sorted.txt")
print("- opchs_filtered_sorted.txt")
