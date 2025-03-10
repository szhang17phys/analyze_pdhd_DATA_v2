import re

# Input file
input_file = "../original_list/updated_initial_print.txt"

# Output files
decay_x_file = "./statResult/updated_decayX.txt"
decay_y_file = "./statResult/updated_decayY.txt"
decay_z_file = "./statResult/updated_decayZ.txt"  # End point of track
michel_score_file = "./statResult/updated_michelScore.txt"
michel_hits_file = "./statResult/updated_michelHits.txt"
michel_truth_file = "./statResult/updated_michelTruth.txt"

# Initialize counters
event_count = 0
track_count = 0
michel_count = 0

# Open files for writing
with open(decay_x_file, "w") as dx, open(decay_y_file, "w") as dy, open(decay_z_file, "w") as dz, \
     open(michel_score_file, "w") as ms, open(michel_hits_file, "w") as mh, open(michel_truth_file, "w") as mt:
    # Read input file line by line
    with open(input_file, "r") as f:
        for line in f:
            line = line.strip()
            
            # Detect event count
            if line.startswith("iEntry (EVENT COUNT)"):
                event_count += 1
            
            # Detect track count
            elif line.startswith("pandorat0 (T0 TRACK COUNT)"):
                track_count += 1
            
            # Detect Michel candidate count
            elif line.startswith("======Michel e CAND! (score>0.03) COUNT======"):
                michel_count += 1
            
            # Extract Michel score & Michel hits
            elif "Michel score:" in line:
                score_match = re.search(r"Michel score: ([0-9\.]+),\s*Michel hits: (\d+)", line)
                if score_match:
                    ms.write(score_match.group(1) + "\n")
                    mh.write(score_match.group(2) + "\n")
            
            # Extract End(x, y, z) values
            elif "End(x, y, z) =" in line:
                end_match = re.search(r"End\(x, y, z\) = \((-?[0-9\.]+), (-?[0-9\.]+), (-?[0-9\.]+)\)", line)
                if end_match:
                    dx.write(end_match.group(1) + "\n")
                    dy.write(end_match.group(2) + "\n")
                    dz.write(end_match.group(3) + "\n")
            
            # Extract True Michel value
            elif "Run:" in line and "True Michel:" in line:
                truth_match = re.search(r"True Michel:\s*(\d+)", line)
                if truth_match:
                    mt.write(truth_match.group(1) + "\n")

# Print counts
print(f"Total Events: {event_count}")
print(f"Total Tracks: {track_count}")
print(f"Total Michel Candidates: {michel_count}")
