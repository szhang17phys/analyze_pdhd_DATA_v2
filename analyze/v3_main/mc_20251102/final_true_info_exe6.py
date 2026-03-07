import re
import os
import sys

# ============================================================
# Get DATE from environment (passed by run.sh)
# ============================================================
DATE = os.getenv("DATE")
if DATE is None:
    print("[ERROR] DATE environment variable not set. Exiting.")
    sys.exit(1)

# Define dynamic output file paths
x_path = f"posX_extract_{DATE}.txt"
y_path = f"posY_extract_{DATE}.txt"
z_path = f"posZ_extract_{DATE}.txt"
E_path = f"energy_extract_{DATE}.txt"
L_path = f"lifetime_extract_{DATE}.txt"
P_path = f"pdg_extract_{DATE}.txt"
S_path = f"michelScore_extract_{DATE}.txt"
H_path = f"michelHits_extract_{DATE}.txt"

# Input file paths
mcTruth_path = os.environ.get("MCTRUTH_PATH", "")
muon_total_path = f"./muon_total_{DATE}.txt"

print("[INFO] DATE variable:", DATE)
print("[INFO] mcTruth path  :", mcTruth_path)
print("[INFO] muon total path:", muon_total_path)

# Open output files in write mode
with open(x_path, "w") as x_out, open(y_path, "w") as y_out, open(z_path, "w") as z_out, \
     open(E_path, "w") as E_out, open(L_path, "w") as L_out, open(P_path, "w") as P_out, \
     open(S_path, "w") as S_out, open(H_path, "w") as H_out:

    #================================================================
    # Load all lines from filtered input into memory
    #================================================================
    with open(mcTruth_path, "r") as f:
        filtered_lines = f.readlines()

    #================================================================
    # Process each line in muon_total_DATE.txt
    #================================================================
    with open(muon_total_path, "r") as f:
        for line in f:
            match = re.search(r"event(\d+)_trackID(\d+)", line)
            if not match:
                continue

            event_target = int(match.group(1))
            track_target = int(match.group(2))

            for i, current_line in enumerate(filtered_lines):
                if "Run:" in current_line and "Event:" in current_line and "TrackID:" in current_line:
                    evt_trk = re.search(r"Event:\s*(\d+),\s*TrackID:\s*(\d+)", current_line)
                    if not evt_trk:
                        continue

                    event = int(evt_trk.group(1))
                    track = int(evt_trk.group(2))

                    if event == event_target and track == track_target:
                        # (Keep all your original extraction logic here, unchanged)
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

                        pdg_match = re.search(r"PDG:\s*([+-]?\d+)", current_line)
                        if pdg_match:
                            P_out.write(pdg_match.group(1) + "\n")
                        else:
                            P_out.write("NaN\n")

                        tl_match = re.search(
                            r"TrueE\[MeV\]:\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?),\s*"
                            r"lifetime\[us\]:\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)",
                            current_line
                        )
                        if tl_match:
                            E_out.write(tl_match.group(1) + "\n")
                            L_out.write(tl_match.group(2) + "\n")
                        else:
                            E_out.write("NaN\n")
                            L_out.write("NaN\n")

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

                        break
