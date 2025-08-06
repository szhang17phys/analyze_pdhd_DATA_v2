import re

# Input file
input_file = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/analyze_pdhd_DATA_v2/statScript/server/MC_202508/michelt0_process_original/print_pdhd_New20250804_MC.txt"

# Output files
decay_x_file = "./extract_initialList/decayX_initial.txt"
decay_y_file = "./extract_initialList/decayY_initial.txt"
decay_z_file = "./extract_initialList/decayZ_initial.txt"  # end point of track
michel_score_file = "./extract_initialList/michelScore_initial.txt"
michel_hits_file = "./extract_initialList/michelHits_initial.txt"
start_x_file = "./extract_initialList/startX_initial.txt"   # start point of track
start_y_file = "./extract_initialList/startY_initial.txt"
start_z_file = "./extract_initialList/startZ_initial.txt"

eventID_file = "./extract_initialList/eventID_initial.txt"
trackID_file = "./extract_initialList/trackID_initial.txt"



# Initialize counters
michel_count = 0

# Open files for writing
with open(decay_x_file, "w") as dx, \
     open(decay_y_file, "w") as dy, \
     open(decay_z_file, "w") as dz, \
     open(michel_score_file, "w") as ms, \
     open(michel_hits_file, "w") as mh, \
     open(start_x_file, "w") as sx, \
     open(start_y_file, "w") as sy, \
     open(start_z_file, "w") as sz, \
     open(eventID_file, "w") as eid, \
     open(trackID_file, "w") as tid:
    
    # Read input file line by line
    with open(input_file, "r") as f:
        for line in f:
            line = line.strip()
            
            # Detect Michel candidate count
            if line.startswith("======Michel e CAND!"):
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
            
            # Extract Vertex(x, y, z) values (start vertex of track)
            elif "Vertex(x, y, z) =" in line:
                start_match = re.search(r"Vertex\(x, y, z\) = \((-?[0-9\.]+), (-?[0-9\.]+), (-?[0-9\.]+)\)", line)
                if start_match:
                    sx.write(start_match.group(1) + "\n")
                    sy.write(start_match.group(2) + "\n")
                    sz.write(start_match.group(3) + "\n")

            # Extract End(x, y, z) values
            elif "End(x, y, z) =" in line:
                end_match = re.search(r"End\(x, y, z\) = \((-?[0-9\.]+), (-?[0-9\.]+), (-?[0-9\.]+)\)", line)
                if end_match:
                    dx.write(end_match.group(1) + "\n")
                    dy.write(end_match.group(2) + "\n")
                    dz.write(end_match.group(3) + "\n")   



# Print counts
print(f"\n===Total Michel Candidates: {michel_count}")

