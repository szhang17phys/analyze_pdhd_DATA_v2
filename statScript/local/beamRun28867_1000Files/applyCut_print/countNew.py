import re

# Input file
input_file = "./filtered_print.txt"

# Output files
decay_x_file = "./newResult/decayX_filtered.txt"
decay_y_file = "./newResult/decayY_filtered.txt"
decay_z_file = "./newResult/decayZ_filtered.txt"#end point of track---
michel_score_file = "./newResult/michelScore_filtered.txt"
michel_hits_file = "./newResult/michelHits_filtered.txt"
start_x_file = "./newResult/startX_filtered.txt"#start point of track---
start_y_file = "./newResult/startY_filtered.txt"
start_z_file = "./newResult/startZ_filtered.txt"

# Initialize counters
michel_count = 0

# Open files for writing
with open(decay_x_file, "w") as dx, open(decay_y_file, "w") as dy, open(decay_z_file, "w") as dz, open(michel_score_file, "w") as ms, open(michel_hits_file, "w") as mh, open(start_x_file, "w") as sx, open(start_y_file, "w") as sy, open(start_z_file, "w") as sz:
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
            
            # Extract End(x, y, z) values
            elif "End(x, y, z) =" in line:
                end_match = re.search(r"End\(x, y, z\) = \((-?[0-9\.]+), (-?[0-9\.]+), (-?[0-9\.]+)\)", line)
                if end_match:
                    dx.write(end_match.group(1) + "\n")
                    dy.write(end_match.group(2) + "\n")
                    dz.write(end_match.group(3) + "\n")

            # Extract Vertex(x, y, z) values (start vertex of track)
            elif "Vertex(x, y, z) =" in line:
                start_match = re.search(r"Vertex\(x, y, z\) = \((-?[0-9\.]+), (-?[0-9\.]+), (-?[0-9\.]+)\)", line)
                if start_match:
                    sx.write(start_match.group(1) + "\n")
                    sy.write(start_match.group(2) + "\n")
                    sz.write(start_match.group(3) + "\n")


# Print counts
print(f"\n===Total Michel Candidates: {michel_count}")

