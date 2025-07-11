import re

# Define output file paths
x_path = "posX_extract_2dot8.txt"
y_path = "posY_extract_2dot8.txt"
z_path = "posZ_extract_2dot8.txt"

# Open output files in write mode to overwrite existing content
with open(x_path, "w") as x_out, open(y_path, "w") as y_out, open(z_path, "w") as z_out:
    
    # Load all lines from print_3000Files_filtered.txt into memory
    with open("/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/analyze_pdhd_DATA_v2/statScript/local/cosmicRun28116_FullRun/applyCut_print/filtered_fullRun_print.txt", "r") as f:
        filtered_lines = f.readlines()

    # Process each line in peakFinder_muonTime_new20250602.txt
    with open("./peakFinder_muonTime_2dot8.txt", "r") as f:
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

                # Look for the line containing both Event and TrackID
                if "Run:" in current_line and "Event:" in current_line and "TrackID:" in current_line:
                    event_match = re.search(r"Event:\s*(\d+),\s*TrackID:\s*(\d+)", current_line)
                    if event_match:
                        event = int(event_match.group(1))
                        track = int(event_match.group(2))

                        if event == event_target and track == track_target:
                            # End(x, y, z) is assumed to be 2 lines below this line
                            if i + 2 < len(filtered_lines):
                                end_line = filtered_lines[i + 2].strip()
                                end_match = re.search(r"\(([-\d\.]+),\s*([-\d\.]+),\s*([-\d\.]+)\)", end_line)
                                if end_match:
                                    x_out.write(end_match.group(1) + "\n")
                                    y_out.write(end_match.group(2) + "\n")
                                    z_out.write(end_match.group(3) + "\n")
                            break  # Stop searching once match is found
