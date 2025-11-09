import os
import re
import argparse
import glob

# ================================================================
# Parse input argument (filtered file)
# ================================================================
parser = argparse.ArgumentParser(description="Extract values from filtered Michel file")
parser.add_argument("--input", required=True, help="Path to the filtered input file")
args = parser.parse_args()

input_file = args.input
print(f"[extractValues.py] Input file: {input_file}")

# ================================================================
# Prepare output directory
# ================================================================
output_dir = "./newResult"
os.makedirs(output_dir, exist_ok=True)

# Remove old output text files before writing new ones
old_files = glob.glob(os.path.join(output_dir, "*.txt"))
if old_files:
    print(f"[extractValues.py] Removing {len(old_files)} old files in {output_dir}/")
    for f in old_files:
        os.remove(f)
else:
    print(f"[extractValues.py] No old output files to remove.")

# ================================================================
# Define output file paths
# ================================================================
decay_x_file = os.path.join(output_dir, "decayX_filtered.txt")
decay_y_file = os.path.join(output_dir, "decayY_filtered.txt")
decay_z_file = os.path.join(output_dir, "decayZ_filtered.txt")  # end point of track
michel_score_file = os.path.join(output_dir, "michelScore_filtered.txt")
michel_hits_file = os.path.join(output_dir, "michelHits_filtered.txt")
start_x_file = os.path.join(output_dir, "startX_filtered.txt")   # start point of track
start_y_file = os.path.join(output_dir, "startY_filtered.txt")
start_z_file = os.path.join(output_dir, "startZ_filtered.txt")
eventID_file = os.path.join(output_dir, "eventID_filtered.txt")
trackID_file = os.path.join(output_dir, "trackID_filtered.txt")
opchs_file_path = os.path.join(output_dir, "opchs_filtered.txt")

# ================================================================
# Process input file and write outputs
# ================================================================
michel_count = 0

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
     open(opchs_file_path, "w") as opchs:

    with open(input_file, "r") as f:
        for line in f:
            line = line.strip()

            # Detect Michel candidate count
            if line.startswith("======Michel e CAND!"):
                michel_count += 1

            # Extract Michel score & hits
            elif "Michel score:" in line:
                score_match = re.search(r"Michel score: ([0-9\.]+),\s*Michel hits: (\d+)", line)
                if score_match:
                    ms.write(score_match.group(1) + "\n")
                    mh.write(score_match.group(2) + "\n")

            # Extract Event and TrackID
            elif "Run:" in line and "Event:" in line and "TrackID:" in line:
                event_track_match = re.search(r"Run:\s*\d+,\s*Event:\s*(\d+),\s*TrackID:\s*(\d+)", line)
                if event_track_match:
                    eid.write(event_track_match.group(1) + "\n")
                    tid.write(event_track_match.group(2) + "\n")

            # Extract End(x, y, z)
            elif "End(x, y, z) =" in line:
                end_match = re.search(r"End\(x, y, z\) = \((-?[0-9\.]+), (-?[0-9\.]+), (-?[0-9\.]+)\)", line)
                if end_match:
                    dx.write(end_match.group(1) + "\n")
                    dy.write(end_match.group(2) + "\n")
                    dz.write(end_match.group(3) + "\n")

            # Extract Vertex(x, y, z)
            elif "Vertex(x, y, z) =" in line:
                start_match = re.search(r"Vertex\(x, y, z\) = \((-?[0-9\.]+), (-?[0-9\.]+), (-?[0-9\.]+)\)", line)
                if start_match:
                    sx.write(start_match.group(1) + "\n")
                    sy.write(start_match.group(2) + "\n")
                    sz.write(start_match.group(3) + "\n")

            # Extract channels (Closest OpCh)
            elif line.startswith("Closest OpCh (y, z):"):
                opch_numbers = []
                for _ in range(3):
                    try:
                        next_line = next(f).strip()
                    except StopIteration:
                        break
                    numbers = re.findall(r"-?\d+(?:\.\d+)?", next_line)
                    opch_numbers.extend(numbers)
                opchs.write(" ".join(opch_numbers) + "\n")

# ================================================================
# Print summary
# ================================================================
print(f"\n=== Total Michel Candidates: {michel_count}")
print(f"[extractValues.py] Output directory: {output_dir}")
