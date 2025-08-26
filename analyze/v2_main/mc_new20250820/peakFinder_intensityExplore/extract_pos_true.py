import re

# Define output file paths
x_path = "posX_extract_20250820.txt"
y_path = "posY_extract_20250820.txt"
z_path = "posZ_extract_20250820.txt"
E_path = "energy_extract_20250820.txt"
L_path = "lifetime_extract_20250820.txt"

# Open output files in write mode
with open(x_path, "w") as x_out, open(y_path, "w") as y_out, open(z_path, "w") as z_out, \
     open(E_path, "w") as E_out, open(L_path, "w") as L_out:

    #================================================================
    # Load all lines from filtered input into memory
    with open("/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/analyze_pdhd_DATA_v2/statScript/local/MC_new202508/add_mcTruth/updated_New20250820_initial.txt", "r") as f:
        filtered_lines = f.readlines()
    #================================================================

    # Process each line in muon_time_20250820.txt
    with open("./muon_time_20250820.txt", "r") as f:
        for line in f:
            # Extract event and trackID from the line
            match = re.search(r"event(\d+)_trackID(\d+)", line)
            if not match:
                continue

            event_target = int(match.group(1))
            track_target = int(match.group(2))

            # Loop through every line in filtered_lines to find a matching Event and TrackID
            for i in range(len(filtered_lines)):
                current_line = filtered_lines[i].strip()

                if "Run:" in current_line and "Event:" in current_line and "TrackID:" in current_line:
                    # Match Event and TrackID
                    evt_trk = re.search(r"Event:\s*(\d+),\s*TrackID:\s*(\d+)", current_line)
                    if not evt_trk:
                        continue

                    event = int(evt_trk.group(1))
                    track = int(evt_trk.group(2))

                    if event == event_target and track == track_target:
                        # Extract TrueE and lifetime (guaranteed present)
                        tl_match = re.search(
                            r"TrueE\[MeV\]:\s*([+-]?\d+(?:\.\d+)?),\s*lifetime\[us\]:\s*([+-]?\d+(?:\.\d+)?)",
                            current_line
                        )
                        E_out.write(tl_match.group(1) + "\n")
                        L_out.write(tl_match.group(2) + "\n")

                        # Extract End(x, y, z) two lines below
                        if i + 2 < len(filtered_lines):
                            end_line = filtered_lines[i + 2].strip()
                            end_match = re.search(
                                r"\(([-\d\.]+),\s*([-\d\.]+),\s*([-\d\.]+)\)", end_line
                            )
                            if end_match:
                                x_out.write(end_match.group(1) + "\n")
                                y_out.write(end_match.group(2) + "\n")
                                z_out.write(end_match.group(3) + "\n")
                        break
