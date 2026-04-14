import re
import argparse


parser = argparse.ArgumentParser(
    description="Extract TPC position / Michel score / Michel hits info matched to muon peak candidates."
)

parser.add_argument("--filtered_txt", required=True, help="Filtered input txt file.")
parser.add_argument("--muon_txt", required=True, help="Muon peak txt file.")

parser.add_argument("--x_out", required=True, help="Output txt for X position.")
parser.add_argument("--y_out", required=True, help="Output txt for Y position.")
parser.add_argument("--z_out", required=True, help="Output txt for Z position.")
parser.add_argument("--score_out", required=True, help="Output txt for Michel score.")
parser.add_argument("--hits_out", required=True, help="Output txt for Michel hits.")

args = parser.parse_args()


# Define output file paths
x_path = args.x_out
y_path = args.y_out
z_path = args.z_out
S_path = args.score_out
H_path = args.hits_out

# Open output files in write mode
with open(x_path, "w") as x_out, open(y_path, "w") as y_out, open(z_path, "w") as z_out, \
     open(S_path, "w") as S_out, open(H_path, "w") as H_out:

    #================================================================
    # Load all lines from filtered input into memory
    #================================================================
    with open(args.filtered_txt, "r") as f:
        filtered_lines = f.readlines()

    #================================================================
    # Process each line in muon_total_202602.txt
    #================================================================
    with open(args.muon_txt, "r") as f:
        for line in f:
            match = re.search(r"event(\d+)_trackID(\d+)", line)
            if not match:
                continue

            event_target = int(match.group(1))
            track_target = int(match.group(2))

            # Search for the corresponding block in filtered_lines
            for i, current_line in enumerate(filtered_lines):
                if "Run:" in current_line and "Event:" in current_line and "TrackID:" in current_line:
                    evt_trk = re.search(r"Event:\s*(\d+),\s*TrackID:\s*(\d+)", current_line)
                    if not evt_trk:
                        continue

                    event = int(evt_trk.group(1))
                    track = int(evt_trk.group(2))

                    # Match event + track
                    if event == event_target and track == track_target:
                        #------------------------------------------------
                        # Extract Michel score and hits (from one line above)
                        #------------------------------------------------
                        if i > 0:
                            prev_line = filtered_lines[i - 1].strip()
                            ms_match = re.search(
                                r"Michel score:\s*([0-9Ee+\-\.]+),\s*Michel hits:\s*(\d+)",
                                prev_line
                            )
                            if ms_match:
                                S_out.write(ms_match.group(1) + "\n")
                                H_out.write(ms_match.group(2) + "\n")
                            else:
                                S_out.write("NaN\n")
                                H_out.write("NaN\n")
                        else:
                            S_out.write("NaN\n")
                            H_out.write("NaN\n")


                        #------------------------------------------------
                        # Extract End(x, y, z) (two lines below)
                        #------------------------------------------------
                        if i + 2 < len(filtered_lines):
                            end_line = filtered_lines[i + 2].strip()
                            end_match = re.search(
                                r"\(([-\d\.]+),\s*([-\d\.]+),\s*([-\d\.]+)\)",
                                end_line
                            )
                            if end_match:
                                x_out.write(end_match.group(1) + "\n")
                                y_out.write(end_match.group(2) + "\n")
                                z_out.write(end_match.group(3) + "\n")
                            else:
                                x_out.write("NaN\n")
                                y_out.write("NaN\n")
                                z_out.write("NaN\n")
                        else:
                            x_out.write("NaN\n")
                            y_out.write("NaN\n")
                            z_out.write("NaN\n")

                        # Stop after finding the first match
                        break

                    