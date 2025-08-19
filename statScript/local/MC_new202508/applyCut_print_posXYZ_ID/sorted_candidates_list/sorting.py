#Moddified by Shu, now the "event" is in fact Michel score!!
#Aug 5, 2025---

# Define file names
decayX_file = "../filtered_results/decayX_filtered.txt"
decayY_file = "../filtered_results/decayY_filtered.txt"
decayZ_file = "../filtered_results/decayZ_filtered.txt"

ms_file = "../filtered_results/michelScore_filtered.txt"
track_file = "../filtered_results/trackID_filtered.txt"
opchs_file = "../filtered_results/opchs_filtered.txt"


# Read the data from all three files
with open(decayX_file, "r") as f_decayX, open(decayY_file, "r") as f_decayY, open(decayZ_file, "r") as f_decayZ, open(ms_file, "r") as f_ms, open(track_file, "r") as f_track, open(opchs_file, "r") as f_opchs:
    decayX_lines = f_decayX.readlines()
    decayY_lines = f_decayY.readlines()
    decayZ_lines = f_decayZ.readlines()
    ms_lines = f_ms.readlines()
    track_lines = f_track.readlines()
    opchs_lines = f_opchs.readlines()

# Convert decayX to float for sorting, keeping all data aligned
# Create a list of tuples---
event_data = [(float(decayX_lines[i].strip()), float(decayY_lines[i].strip()), float(decayZ_lines[i].strip()), float(ms_lines[i].strip()), track_lines[i].strip(), opchs_lines[i].strip()) for i in range(len(decayX_lines))]

# Sort based on decayX_lines (first element of the tuple)
# Ascending order is the default for sort() in Python---
event_data.sort(key=lambda x: x[0])

# Write sorted data back to files
with open("decayX_filtered_sorted.txt", "w") as f_decayX_out, \
     open("decayY_filtered_sorted.txt", "w") as f_decayY_out, \
     open("decayZ_filtered_sorted.txt", "w") as f_decayZ_out, \
     open("ms_filtered_sorted.txt", "w") as f_ms_out, \
     open("trackID_filtered_sorted.txt", "w") as f_track_out, \
     open("opchs_filtered_sorted.txt", "w") as f_opchs_out:

    for decayX, decayY, decayZ, ms, track, opchs in event_data:
        f_decayX_out.write(f"{decayX}\n")       # Write 
        f_decayY_out.write(f"{decayY}\n")       # Write 
        f_decayZ_out.write(f"{decayZ}\n")       # Write
        f_ms_out.write(f"{ms}\n")       # Write 
        f_track_out.write(f"{track}\n")       # Write track ID
        f_opchs_out.write(f"{opchs}\n")       # Write full line of opchs values

print("Sorting complete. Sorted files saved as:")
print("- decayX_filtered_sorted.txt")
print("- decayY_filtered_sorted.txt")
print("- decayZ_filtered_sorted.txt")
print("- ms_filtered_sorted.txt")
print("- trackID_filtered_sorted.txt")
print("- opchs_filtered_sorted.txt")
