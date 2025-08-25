import re

# Input file
input_file = "./updated_New20250820_initial.txt"

# Output files
decay_x_file = "./extract_initialList/decayX_New20250820_initial.txt"
decay_y_file = "./extract_initialList/decayY_New20250820_initial.txt"
decay_z_file = "./extract_initialList/decayZ_New20250820_initial.txt"  # end point of track
michel_score_file = "./extract_initialList/michelScore_New20250820_initial.txt"
michel_hits_file = "./extract_initialList/michelHits_New20250820_initial.txt"
start_x_file = "./extract_initialList/startX_New20250820_initial.txt"   # start point of track
start_y_file = "./extract_initialList/startY_New20250820_initial.txt"
start_z_file = "./extract_initialList/startZ_New20250820_initial.txt"

eventID_file = "./extract_initialList/eventID_New20250820_initial.txt"
trackID_file = "./extract_initialList/trackID_New20250820_initial.txt"

energy_file = "./extract_initialList/energy_New20250820_initial.txt"
lifetime_file = "./extract_initialList/lifetime_New20250820_initial.txt"

# Initialize counters
michel_count = 0

# Regex for floats (accepts decimals and scientific notation)
FLOAT = r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?'
MICHEL_RE = re.compile(rf'Michel score:\s*({FLOAT}),\s*Michel hits:\s*(\d+)')

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
     open(trackID_file, "w") as tid, \
     open(energy_file, "w") as Eid, \
     open(lifetime_file, "w") as Lid:     
    
    # Read input file line by line
    with open(input_file, "r") as f:
        for line in f:
            line = line.strip()
            
            # Detect Michel candidate count
            if line.startswith("======Michel e CAND!"):
                michel_count += 1
            
            # Extract Michel score & Michel hits
            elif "Michel score:" in line:
                score_match = MICHEL_RE.search(line)
                if score_match:
                    ms.write(score_match.group(1) + "\n")
                    mh.write(score_match.group(2) + "\n")
            
            # Extract Run / Event / TrackID / TrueE / lifetime
            elif "Run:" in line and "Event:" in line and "TrackID:" in line and "TrueE[MeV]" in line and "lifetime" in line:
                try:
                    parts = line.split(':')
                    # Expect: ['Run', ' 1000,  Event', ' 1837,  TrackID', ' 14,   TrueE[MeV]', ' 47.5884,  lifetime[us]', ' 0.369245']
                    run_val = int(parts[1].split(',')[0].strip())
                    event_val = int(parts[2].split(',')[0].strip())
                    track_val = int(parts[3].split(',')[0].strip())
                    trueE_val = float(parts[4].split(',')[0].strip())
                    lifetime_val = float(parts[5].strip())

                    eid.write(f"{event_val}\n")
                    tid.write(f"{track_val}\n")
                    Eid.write(f"{trueE_val}\n")
                    Lid.write(f"{lifetime_val}\n")

                except Exception as e:
                    print(f"❌ Parsing failed for line:\n{line}\nError: {e}")



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
