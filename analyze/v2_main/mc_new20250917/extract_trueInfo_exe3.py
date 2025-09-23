import re

# Define output file paths
E_path  = "print_trueE20250917.txt"
PDG_path = "print_truePDG20250917.txt"

# Open output files in write mode
with open(E_path, "w") as E_out, open(PDG_path, "w") as PDG_out:

    # ================================================================
    # Load all lines from the mcTruth input into memory
    # ================================================================
    with open("/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/analyze_pdhd_DATA_v2/statScript/local/MC_new202509/add_mcTruth_npMichel/updated_New20250917_initial.txt", "r") as f:
        filtered_lines = f.readlines()

    # ================================================================
    # Process each line in the wvfCoin count file
    # ================================================================
    with open("./print_wvfCoin_count20250917.txt", "r") as f:

        for line in f:
            # Extract event and trackID from filenames like:
            # wvfFind_event2036_trackID20_opNum1_6.root: 1
            # wvfFind_event3700_trackID2_opNum5_merged.root: 9
            match = re.search(r"event(\d+)_trackID(\d+)", line)
            if not match:
                continue

            event_target = int(match.group(1))
            track_target = int(match.group(2))

            # Scan the mcTruth lines to find a matching Event and TrackID
            for i in range(len(filtered_lines)):
                current_line = filtered_lines[i].strip()

                # Example line:
                # Run: 5,  Event: 6044,  TrackID: 1,  PDG: -11,  TrueE[MeV]: 26.2607,  lifetime[us]: 1.70662
                if "Run:" in current_line and "Event:" in current_line and "TrackID:" in current_line:
                    evt_trk = re.search(r"Event:\s*(\d+),\s*TrackID:\s*(\d+)", current_line)
                    if not evt_trk:
                        continue

                    event = int(evt_trk.group(1))
                    track = int(evt_trk.group(2))

                    if event == event_target and track == track_target:
                        # ---- Extract PDG ----
                        pdg_match = re.search(r"PDG:\s*([+-]?\d+)", current_line)
                        if pdg_match:
                            PDG_out.write(pdg_match.group(1) + "\n")

                        # ---- Extract TrueE ----
                        trueE_match = re.search(
                            r"TrueE\[MeV\]:\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)",
                            current_line
                        )
                        if trueE_match:
                            E_out.write(trueE_match.group(1) + "\n")

                        # Stop searching once match is found
                        break
