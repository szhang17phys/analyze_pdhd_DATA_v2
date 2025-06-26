import re

# Input file
input_file = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/analyze_pdhd_DATA_v2/statScript/server/beamRun28891_FullRun/michelt0_process_original/fullRun_initial_processing.txt"

# Output files
decay_x_file = "./decayX.txt"
decay_y_file = "./decayY.txt"
decay_z_file = "./decayZ.txt"  # end point of track


# Initialize counters
michel_count = 0

# Open files for writing
with open(decay_x_file, "w") as dx, \
     open(decay_y_file, "w") as dy, \
     open(decay_z_file, "w") as dz:
    
    # Read input file line by line
    with open(input_file, "r") as f:
        for line in f:
            line = line.strip()
            
            # Detect Michel candidate count
            if line.startswith("======Michel e CAND!"):
                michel_count += 1
            
            # Extract End(x, y, z) values
            elif "End(x, y, z) =" in line:
                end_match = re.search(r"End\(x, y, z\) = \((-?[0-9\.]+), (-?[0-9\.]+), (-?[0-9\.]+)\)", line)
                if end_match:
                    dx.write(end_match.group(1) + "\n")
                    dy.write(end_match.group(2) + "\n")
                    dz.write(end_match.group(3) + "\n")


# Print counts
print(f"\n===Total Michel Candidates: {michel_count}")

