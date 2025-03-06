import re

# Input file
input_file = "./filtered_print.txt"

# Output files
decay_x_file = "./newResult/decayX_filtered.txt"
decay_y_file = "./newResult/decayY_filtered.txt"
decay_z_file = "./newResult/decayZ_filtered.txt"  # end point of track
michel_score_file = "./newResult/michelScore_filtered.txt"
michel_hits_file = "./newResult/michelHits_filtered.txt"

eventID_file = "./newResult/eventID_filtered.txt"
trackID_file = "./newResult/trackID_filtered.txt"

opchs_file_path = "./newResult/opchs_filtered.txt"

# Initialize counters
michel_count = 0

# Open files for writing
with open(decay_x_file, "w") as dx, \
     open(decay_y_file, "w") as dy, \
     open(decay_z_file, "w") as dz, \
     open(michel_score_file, "w") as ms, \
     open(michel_hits_file, "w") as mh, \
     open(eventID_file, "w") as eid, \
     open(trackID_file, "w") as tid, \
     open(opchs_file_path, "w") as opchs:
    
    # Read input file line by line
    with open(input_file, "r") as f:
        for line in f:
            line = line.strip()
            
            # Detect Michel candidate count
            if line.startswith("======Michel e CAND! (score>0.03) COUNT======"):
                michel_count += 1
            
            # Extract Michel score & Michel hits
            elif "Michel score:" in line:
                score_match = re.search(r"Michel score: ([0-9\.]+),\s*Michel hits: (\d+)", line)
                if score_match:
                    ms.write(score_match.group(1) + "\n")
                    mh.write(score_match.group(2) + "\n")
            
            # Extract Event and TrackID values from the "Run:" line
            elif "Run:" in line and "Event:" in line and "TrackID:" in line:
                event_track_match = re.search(r"Run:\s*\d+,\s*Event:\s*(\d+),\s*TrackID:\s*(\d+)", line)
                if event_track_match:
                    eid.write(event_track_match.group(1) + "\n")
                    tid.write(event_track_match.group(2) + "\n")
            
            # Extract End(x, y, z) values
            elif "End(x, y, z) =" in line:
                end_match = re.search(r"End\(x, y, z\) = \((-?[0-9\.]+), (-?[0-9\.]+), (-?[0-9\.]+)\)", line)
                if end_match:
                    dx.write(end_match.group(1) + "\n")
                    dy.write(end_match.group(2) + "\n")
                    dz.write(end_match.group(3) + "\n")
            
            # Extract channels numbers after "Closest OpCh (y, z):"
            elif line.startswith("Closest OpCh (y, z):"):
                # Assume the next three lines contain the channel numbers
                opch_numbers = []
                for _ in range(3):
                    try:
                        next_line = next(f).strip()
                    except StopIteration:
                        break
                    # Find all numbers (integers or decimals) in the line
                    numbers = re.findall(r"-?\d+(?:\.\d+)?", next_line)
                    opch_numbers.extend(numbers)
                # Write all nine values in a single line, separated by spaces
                opchs.write(" ".join(opch_numbers) + "\n")

# Print counts
print(f"\n===Total Michel Candidates: {michel_count}")

